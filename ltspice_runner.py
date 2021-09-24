import os, subprocess, sys, re
import numpy as np
import pandas as pd
from parse_utils import parse_netlist, write_netlist
import re
from datetime import datetime
from struct import unpack
import matplotlib.pyplot as plt

"""
LTspiceRunner is responsible for a given netlist, cir or asc file.
It can create a netlist out of asc files, if possible.
"""
class LTSpiceRunner:

    def __init__(self, path: str) -> None:
        # See whether it;s a netlist, asc or cir file.
        # If it's a asc file, create a netlist from it.
        # Detect the os.
        try: 
            self.dirname, self.basename = os.path.dirname(path), os.path.basename(path)
            if sys.platform == 'darwin':
                self._ltspice = "/Applications/LTspice.app/Contents/MacOS/LTspice"
                self._cmd_separator = "; "
            elif sys.platform == 'win32':
                self._ltspice = '"C:\\Program Files\\LTC\\LTspiceXVII\\XVIIx64.exe"'
                self._cmd_separator = " && "
            else:
                self._ltspice = None
                raise NotImplementedError("Platforms other than Mac are not implemented yet")
        except Exception as e:
            raise e

    def get_basename(self):
        return self.basename
    
    def get_dirname(self):
        return self.dirname
    
    def get_fullname(self):
        return os.path.join(self.dirname, self.basename)

    def _create_sweep_command(self, input_samples: pd.DataFrame, sweep_param_name='Rx'):
        """
        Creates the sweep command based on the rows of the `input_samples`
        """
        nrows = len(input_samples)
                  
        # First line .step command
        nsamples_str = " ".join([str(x+1) for x in range(nrows)])
        param_line = f".step param {sweep_param_name} list {nsamples_str}"    

        # lambda for pasting the index with the value with a comma
        values_fn = lambda inpt: ','.join(
            str(idx) + ',' + str(val) 
            for idx, val in zip(range(1, nrows+1), inpt))
        
        # Parameters command for the sweep
        values_lines = [
            f".param {col} table({sweep_param_name}, {values_fn(input_samples[col])})"
            for col in input_samples]

        return param_line, values_lines


    def add_sweep(self, input_samples: pd.DataFrame, sweep_param_name='Rx'):
        """
        Appends the netlist with sweep command created from the `input_samples`.
        """
        param, values = self._create_sweep_command(input_samples, sweep_param_name)
        # Read the netlist
        netlist = parse_netlist(self.get_fullname())
        # Add this before the .backanno command
        # Should also add some kind of marker.
        for idx, command in enumerate(netlist):
            if re.match('.backanno', command):
                netlist.insert(idx, "* Sweep added by me")
                netlist.insert(idx + 1, param)
                end_idx = idx + 2
                for idy, value in enumerate(values):
                    netlist.insert(idx+idy+2, value)
                    end_idx = idx+idy+3
                netlist.insert(end_idx, '* Finished adding')
                break

        try: 
            write_netlist(netlist, self.get_fullname())
            return True
        except Exception as e:
            raise e


    def run(self, timeout=20, ascii=True):
        try:
            if self._ltspice is not None:
                cmd =  self._cmd_separator.join([
                    f"cd {self.dirname if len(self.dirname) > 0 else '.'}",
                    f"{self._ltspice} {'-ascii' if ascii else ''} -b {self.basename}"])
                A = subprocess.run(cmd, 
                            shell=True, check=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
                assert isinstance(A, subprocess.CompletedProcess)

        except Exception as e:
            raise e
    
"""
LTspice reader is responsible for reading the log and raw files run by the LTSpiceRunner instance.
The data format is the numpy arrays or pandas dataframes.
"""
class LTSpiceReader:

    def __init__(self, runner: LTSpiceRunner) -> None:
        self.runner = runner


    def parse_log(self, print_encoding=False):
        log_path = re.sub(r'.asc$|.cir$|.net$', r'.log', self.runner.get_fullname())
        if os.path.exists(log_path):
            # Guess encoding
            with open(log_path, 'rb') as file:
                first_bytes = file.read(8)
                if first_bytes.decode('utf8') == 'Circuit:':
                    encoding='utf8'
                elif first_bytes.decode('utf-16 le') == 'Circ':
                    encoding='utf-16 le'
                else:
                    encoding=None
                    raise UnicodeEncodeError(f'Uknown encoding of the log file {log_path}')
            file.close()

            if encoding is not None and file.closed:
                if print_encoding:
                    print(f'The encoding of the file is: {encoding}') 
                try:
                    with open(log_path, 'r', encoding=encoding) as file:
                        lines = file.read().split('\n')
                    file.close()
                    return lines
                except Exception as e:
                    print(e)
        else:
            raise FileNotFoundError(f'Log file {log_path} does not exist.')
    

    def parse_raw(self, columns=None):
        # Find if it's ascii or not -- need to find a flag with Binary or Data
        # Assume that the encoding is utf-16 le. Read 2 bytes at a time. -- assume that it is not ascii for now.
        # For now, simply append the string chain. We will think about the rest and optimizatoin later.
        raw_path = re.sub(r'.net$', '.raw', self.runner.get_fullname())
        encoding = self._guess_encoding(raw_path)
        with open(raw_path, 'rb') as file:
            header_lines = self._parse_until_data(file, encoding)
            header_dict = self._header_to_dict(header_lines)
            # Now parse the binary data
            parsed_data = self._parse_data(file, header_dict, columns)
        return header_dict, parsed_data

    def parse_header(self):
        raw_path = re.sub(r'.net$', '.raw', self.runner.get_fullname())
        encoding = self._guess_encoding(raw_path)
        with open(raw_path, 'rb') as file:
            header_lines = self._parse_until_data(file, encoding)
            header_dict = self._header_to_dict(header_lines)
        file.close()
        return header_dict
    
    def _guess_encoding(self, raw_path):
        with open(raw_path, 'rb') as file:
            first_6_bytes = file.read(6)
            if first_6_bytes.decode('utf8') == 'Title:':
                encoding = 'utf8'
            elif first_6_bytes.decode('utf-16-le') == 'Tit':
                encoding = 'utf-16 le'
            else:
                encoding = None
                raise Exception("Couldn't find encoding of the raw file.")
        file.close()
        return encoding

    def _parse_until_data(self, file, encoding):
        # Intizalize the variables
        lines, sep, data_line = [], "\n", 'Binary:'
        # Buffer to append
        buffer = ''
        while True:
            if self._is_enc16le(encoding):
                decoded = self._read_byte16(file)
            elif self._is_enc8(encoding):
                decoded = self._read_byte8(file)
            else: 
                raise Exception('Unknown encoding.')

            if decoded == sep:
                lines.append(buffer)
                if buffer == data_line:
                    break
                buffer = ''
            else:
                buffer += decoded
        return lines


    def _parse_data(self, file, header_dict, columns=None, add_step_info=True):
        # This assumes that we are reading binary -- not compressed verions for now.
        # and that the current position of the file is just on it.
        # We are also assuming that there is an existing header, 
        # to get the names of the variables and the flag (real or complex)
        # We need to get the number of steps as well.
        # TODO: Define which columns we'd like to read (?)
        no_points = int(header_dict['No. Points'])

        # Variables
        variables = header_dict['Variables']
        if columns:
            funcol = lambda column: variables[variables['Variable'].str.match(re.escape(column))]['Variable'].tolist()[0]
            if type(columns) is list:
                variables = [funcol(column) for column in columns]
            else:
                variables = funcol(columns)
        else:
            variables = variables['Variable'].tolist()
        
        # Preallocate the datafrane
        data_df = pd.DataFrame({
            name: range(no_points) for name in variables},
            dtype='complex128' if self._is_ac_analysis(header_dict) else 'float64')

        if self._is_transient_analysis(header_dict):
            for i in range(int(no_points)):
                # If there are any steps, the number of point has to be divided by the number of steps.
                # The information about the number of steps is present in the log file.
                # However, this infomation can be added in the end to the dataframe as additional column.
                for idx, name in enumerate(header_dict['Variables']['Variable']):
                    if idx == 0:
                        data_df.at[i, name] = self._read8(file)
                    elif name in variables:
                        data_df.at[i, name] = self._read4(file)
                    else:
                        self._read4(file)
                        pass

        elif self._is_ac_analysis(header_dict):
            raise NotImplementedError('AC analysis is not implemented yet')

        # Append the information about the number of steps if needed
        if add_step_info and self._is_stepped(header_dict):
            # no_steps = self._get_steps(num_only=True)
            # The information about the start of the step should be given by the column `time`
            offset = header_dict['Offset']
            x = data_df[data_df['time'] == offset].index.values.tolist()
            x.append(len(data_df))
            x = np.diff(x)
            data_df.insert(len(data_df.columns),
                           'step_no',
                           np.repeat(range(len(x)), x)) 
        return data_df

    def _get_steps(self, num_only=False):
        """
        Creates a dictionary of steps with appropriate information
        """
        log_lines = self.parse_log(print_encoding=False)
        # Filter lines with .step command
        step_lines = [line for line in log_lines if re.match('^.step', line, re.IGNORECASE)]
        if num_only:
            return len(step_lines)
        
        # Split the steps to find the information about the stepped data
        

    def _is_stepped(self, header_dict):
        return any(re.match('stepped', line, re.IGNORECASE) for line in header_dict['Flags'])

    def _read4(self, file):
        return unpack('f', file.read(4))[0]
    
    def _read8(self, file):
        return unpack('d', file.read(8))[0]

    def _read16(self, file):
        return unpack('dd', file.read(16))

    def _is_complex(self, header_dict):
        return any(re.match('complex', line, re.IGNORECASE) for line in header_dict['Flags'])

    def _is_real(self, header_dict):
        return any(re.match('real', line, re.IGNORECASE) for line in header_dict['Flags'])

    def _is_transient_analysis(self, header_dict):
        return re.match('Transient', header_dict['Plotname'], re.IGNORECASE)

    def _is_ac_analysis(self, header_dict):
        return re.match('AC', header_dict['Plotname'], re.IGNORECASE)

    def _header_to_dict(self, header_lines):
        # Create a dictionary of results
        # Stop at the flag "Binary".
        header_dict = {}
        variables_idx = None
        for idx, line in enumerate(header_lines):
            searched = re.search(r'([A-Za-z\. ]+):(.*)$', line)
            key, value = searched.group(1).strip(), searched.group(2).strip()
            # Some values are numerical, such no. points, no. variables etc.
            if re.match(r'No. Variables|No. Points|Offset', key, re.IGNORECASE):
                # Cast to number
                value = float(value)
            elif re.match(r'Date', key, re.IGNORECASE):
                # Create a datetime object
                value = datetime.strptime(value, "%a %b %d %H:%M:%S %Y")
            elif re.match(r'Flags', key, re.IGNORECASE):
                # Flags should be separated
                value = value.split(" ")
            elif re.match(r'^Variable', key, re.IGNORECASE):
                # The rest until `Data` flag should be the variable description
                variables_idx = idx+1
                break
            
            # Append the dictionary
            header_dict[key] = value
        
        if variables_idx is not None:
            # Variables should be the last thing before `Data` flag
            # and `Data` flag is the last thing in `header_lines`
            # Key should be 'variables'
            header_dict[key] = pd.DataFrame([
                line.strip().split('\t')[1:] for line in header_lines[variables_idx:(len(header_lines)-1)]],
                columns=['Variable', 'Description'])
        
        return header_dict


    def _is_enc16le(self, encoding):
        return re.match(r"UTF( |-){0,1}16( |-){0,1}LE", encoding.upper())

    def _is_enc8(self, encoding):
        return re.match(r"UTF( |-){0,1}8", encoding.upper())

    def _read_byte16(self, file):
        return file.read(2).decode('utf-16 le')
    
    def _read_byte8(self, file):
        return file.read(1).decode('utf8')

                



if __name__=='__main__':
    netlist_path = 'ltspice_files/Lisn_sym_copy.net'
    ltrunner = LTSpiceRunner(netlist_path)
    # ltrunner.run(ascii=False)
    ltreader = LTSpiceReader(ltrunner)
    header_dict, parsed_data = ltreader.parse_raw(columns=['V(n006)', 'Ix(u1:LOUT)'])
    print(parsed_data)
    
    ax = parsed_data[parsed_data['step_no']==0].plot(x='time', y = 'V(n006)', c='magenta')
    parsed_data[parsed_data['step_no']==1].plot(x='time', y = 'V(n006)', c='cyan', ax=ax)
    plt.show()

