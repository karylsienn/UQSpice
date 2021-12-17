import os, subprocess, sys, re
import numpy as np
from numpy.core.numeric import full
import pandas as pd
from parse_utils import ENC_UTF16LE, ENC_UTF8, parse_binary, parse_header, parse_netlist, write_netlist, parse_log
import re
from datetime import datetime
from struct import unpack
import matplotlib.pyplot as plt
from random import random

"""
LTspiceRunner is responsible for a given netlist, cir or asc file.
It can create a netlist out of asc files, if possible.
"""
class LTSpiceRunner:

    def __init__(self, path: str) -> None:
        # See whether it;s a netlist, asc or cir file.
        # If it's a asc file, create a netlist from it.
        # Detect the os.
        self.hash = hash(random())
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

    def __hash__(self):
        return self.hash

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
                netlist.insert(idx, f"* Sweep added by LTSpiceRunner {self.hash}")
                netlist.insert(idx + 1, param)
                end_idx = idx + 2
                for idy, value in enumerate(values):
                    netlist.insert(idx+idy+2, value)
                    end_idx = idx+idy+3
                netlist.insert(end_idx, f'* Finished sweep by LTSpiceRunner {self.hash}')
                break
        try: 
            write_netlist(netlist, self.get_fullname())
            return True
        except Exception as e:
            raise e
    
    def clean_sweeps(self):
        netlist = parse_netlist(self.get_fullname())
        en = enumerate(netlist)
        for idx, command in en:
            if re.match(re.escape(f"* Sweep added by LTSpiceRunner {self.hash}"), command):
                start_idx = idx
            elif re.match(re.escape(f"* Finished sweep by LTSpiceRunner {self.hash}"), command):
                end_idx = idx
                break
            else:
                pass            

        while start_idx <= end_idx:
            netlist.pop(start_idx)
            end_idx -= 1

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
                if isinstance(A, subprocess.CompletedProcess):
                    return True
                else:
                    return False

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
        # Handle creation if the runner has not been called yet. Especially
        # that the Reader does not have to be used only with conjuction with a specific runner.
        self.parse_header()
        self.parse_log()  
        # Are there any meas or four commands?
        fullname = self.runner.get_fullname()
        netlist = parse_netlist(fullname)
        self.no_measurements = 0
        self.no_four = False
        for command in netlist:
            if re.match('.meas', command, re.IGNORECASE):
                self.no_measurements += 1
            elif re.match('.four', command, re.IGNORECASE):
                self.no_four +=1


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

        # Data frame of the LTSpice data
        self.data_df = parse_binary(
            raw_path, no_points, no_variables,
            index_start=index_start, col_idx=col_idx, col_names=columns,
            dtype=dtype, header_encoding=header_encoding)
        
        # Add information about step
        if add_step:
            # LTSpice can produce different number of points between different steps
            # Since we need to find the first element which is greater or equal to the offset.
            x = self.data_df[self.data_df['time'] == offset].index.values.tolist()
            x.append(len(self.data_df))
            x = np.diff(x)
            self.data_df.insert(
                len(self.data_df.columns),
                'step_no',
                np.repeat(range(len(x)), x))
        # TODO: interpolate data frames
        # TODO: Depending on the type of analysis we should have either first column `time` of `frequency`
        # Return straightaway   
        return self.data_df

    def get_four_table(self):
        if not self.four:
            raise ValueError("There is no .four statements")
        else:
            pass

    def get_steps(self, num_only=False):
        """
        Creates a dictionary of steps with appropriate information
        """
        if self.log is None:
            self.parse_log()
        # Filter lines with .step command
        step_lines = [line for line in self.log if re.match('^.step', line, re.IGNORECASE)]
        no_steps = len(step_lines)
        if num_only:
            return no_steps
        # Split the steps to find the information about the stepped data
        # Have to read the steps from the netlist and from the log simultaneously.
        # Find sweep added by this ltrunner instance and get it.
        runnerhash = self.runner.hash
        # Read line by line and find only those, which have the hash of this runner
        netlist_lines = parse_netlist(self.runner.get_fullname(),
                                      encoding=ENC_UTF16LE)
        found_sweep, step_info = False, []
        for line in netlist_lines:
            if re.match(f"* Sweep added by LTSpiceRunner {runnerhash}", line):
                found_sweep = True
            elif found_sweep:
                step_info.append(line)
            elif re.match(f"* Finished sweep by LTSpiceRunner {runnerhash}", line):
                break
        # Next line should correspond to .step
        # Get the stepping variable name from it
        stepname = re.search(".step param (.*) ", step_info[0], re.IGNORECASE)
        if stepname:
            stepname = stepname.group(1)
        else:
            raise ValueError("I don't see the stepname.")

        # Define instead of one-liner to handle errors as well.
        def namefun(line):
            searched = re.search('.param (.*) table', line, re.IGNORECASE)
            if searched:
                return searched.group(1)
            else:
                raise ValueError("I don't see the parameter.")

        step_df = pd.DataFrame({
            namefun(line): range(no_steps) for line in step_info[1:]
            }, dtype='float64')
        # Create a dataframe with as many columns as variables
        for name, line in zip(step_df.keys(),step_info[1:]):
            # Get all the variables in this line
            inline = re.search(f"table\({stepname},(.*)\)")
            if inline:
                inline = inline.group(1).strip().split(",")
                # Take only the odd parts
                values = [float(value.strip())
                          for idx, value in enumerate(inline) if idx % 2 == 1]
                step_df[name] = values
        # Put `step` as the first column
        step_df.insert(0, 'step', range(no_steps))
        self.step_df = step_df
        return self.step_df
            
    
    def get_variable_names(self):
        return self.header['Variables']['Variable']

    def any_four(self):
        return self.no_four > 0

    def any_meas(self):
        return self.no_measurements > 0

    def _is_stepped(self, header_dict):
        return any(re.match('stepped', line, re.IGNORECASE) for line in self.header['Flags'])

    def _is_complex(self):
        return any(re.match('complex', line, re.IGNORECASE) for line in self.header['Flags'])

    def _is_real(self):
        return any(re.match('real', line, re.IGNORECASE) for line in self.header['Flags'])

    def _is_transient_analysis(self):
        return re.match('Transient', self.header['Plotname'], re.IGNORECASE)

    def _is_ac_analysis(self):
        return re.match('AC', self.header['Plotname'], re.IGNORECASE)

                

if __name__=='__main__':

    netlist_path = '/Users/karolniewiadomski/Documents/SCENT/Research/Toolbox/UQSpice_0.02/ltspice_files/raport01/Lisn_sym_copy.net'
    ltrunner = LTSpiceRunner(netlist_path)
    # sweepdf = pd.DataFrame({
    #     'C1': [1,2],
    #     'R1': [2,3]
    # })
    # ltrunner.add_sweep(sweepdf)
    # ltrunner.run(timeout=10)
    # removed = ltrunner.clean_sweeps()

    # ltrunner.run(ascii=False)
    ltreader = LTSpiceReader(ltrunner)
    print(ltreader.any_four())
    # parsed_data = ltreader.parse_raw(columns=['time','V(n006)','Ix(u1:LOUT)'], add_step=False)
    # print(parsed_data)
    
    # ax = parsed_data[parsed_data['step_no']==0].plot(x='time', y = 'V(n006)', c='magenta')
    # parsed_data[parsed_data['step_no']==1].plot(x='time', y = 'V(n006)', c='cyan', ax=ax)
    # plt.show()

