import os, subprocess, sys, re
import numpy as np
from numpy.core.numeric import full
import pandas as pd
from parse_utils import parse_binary, parse_header, parse_netlist, write_netlist, parse_log
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
                raise NotImplementedError("Platforms other than Mac and Windows are not implemented yet")
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


    def run(self, timeout=20, ascii=False):
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
        # The assumption that the runner has already run the program.
        self.parse_header()
        self.parse_log()


    def parse_log(self):
        fullname = self.runner.get_fullname()
        log_path = re.sub(r'.net$|.asc$|.cir$', r'.log', fullname)
        self.log = parse_log(log_path)
        return self.log

    def parse_header(self):
        fullname = self.runner.get_fullname()
        raw_path = re.sub(r'.net$|.cir$|.asc$', r'.raw', fullname)
        self.header = parse_header(raw_path)
        return self.header


    def parse_raw(self, columns=None, add_step=True, interpolate=False):
        # Find if it's ascii or not -- need to find a flag with Binary or Data
        # Assume that the encoding is utf-16 le. Read 2 bytes at a time. -- assume that it is not ascii for now.
        # For now, simply append the string chain. We will think about the rest and optimizatoin later.
        fullname = self.runner.get_fullname()
        raw_path = re.sub(r'.net$|.cir$|.asc$', r'.raw', fullname)
        header_encoding = self.header["Encoding"]
        no_points = int(self.header["No. Points"])
        no_variables = int(self.header["No. Variables"])
        index_start = int(self.header["No. Lines"])
        offset = self.header["Offset"]

        # Find the indexes of the columns we want to look at
        all_columns = self.get_variable_names()
        col_idx = [idx for idx, name in enumerate(all_columns) if (name in columns)]
        
        # Find the data type
        if self._is_real():
            dtype = 'float64'
        elif self._is_complex():
            dtype = 'complex128'
        else:
            raise ValueError("Unknown data type.")

        # Data frame of the LTSpice datas
        self.data_df = parse_binary(
            raw_path, no_points, no_variables,
            index_start=index_start, col_idx=col_idx, col_names=columns,
            dtype=dtype, header_encoding=header_encoding)
        
        print(self.data_df[self.data_df['time'] == offset])

        # Add information about step
        if add_step:
            # LTSpice can produce different number of points between different steps
            x = self.data_df[self.data_df['time'] == offset].index.values.tolist()
            x.append(len(self.data_df))
            x = np.diff(x)
            self.data_df.insert(
                len(self.data_df.columns),
                'step_no',
                np.repeat(range(len(x)), x))
        
        # TODO: interpolate data frames
        # Return straigthaway   
        return self.data_df


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
    
    def get_variable_names(self):
        return self.header['Variables']['Variable']

    def any_meas(self, header_dict):
        return any(re.match('meas', line, re.IGNORECASE) for line in header_dict['Flags'])

    def _is_stepped(self, header_dict):
        return any(re.match('stepped', line, re.IGNORECASE) for line in header_dict['Flags'])

    def _read4(self, file):
        """
        Read the real data saved in 4 bytes.
        """
        return unpack('f', file.read(4))[0]
    
    def _read8(self, file):
        """
        Read the timestamp or the frequency, saved as 8 bytes.
        """
        return unpack('d', file.read(8))[0]

    def _read16(self, file):
        """
        Read the complex data, saved in two 8-bytes chunks (for real and imaginary parts)
        """
        return unpack('dd', file.read(16))

    def _is_complex(self):
        return any(re.match('complex', line, re.IGNORECASE) for line in self.header['Flags'])

    def _is_real(self):
        return any(re.match('real', line, re.IGNORECASE) for line in self.header['Flags'])

    def _is_transient_analysis(self):
        return re.match('Transient', self.header['Plotname'], re.IGNORECASE)

    def _is_ac_analysis(self):
        return re.match('AC', self.header['Plotname'], re.IGNORECASE)

                

if __name__=='__main__':
    netlist_path = 'ltspice_files/Lisn_sym_copy.net'
    ltrunner = LTSpiceRunner(netlist_path)
    # ltrunner.run(ascii=False)
    ltreader = LTSpiceReader(ltrunner)
    parsed_data = ltreader.parse_raw(columns=['time','V(n006)','Ix(u1:LOUT)'], add_step=False)
    print(parsed_data)
    
    # ax = parsed_data[parsed_data['step_no']==0].plot(x='time', y = 'V(n006)', c='magenta')
    # parsed_data[parsed_data['step_no']==1].plot(x='time', y = 'V(n006)', c='cyan', ax=ax)
    # plt.show()

