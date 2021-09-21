import enum
import os, subprocess, sys, re
import pandas as pd
from parse_utils import parse_netlist, write_netlist
import re

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


    def _run(self, timeout=20, ascii=True):
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


    def _parse_log(self, print_encoding=False):
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
    

    def _parse_raw(self):
        # Find if it's ascii or not -- need to find a flag with Binary or Data
        # Assume that the encoding is utf-16 le. Read 2 bytes at a time. -- assume that it is not ascii for now.
        # For now, simply append the string chain. We will think about the rest and optimizatoin later.
        raw_path = re.sub(r'.net$', '.raw', self.runner.get_fullname())
        
        # Guess encoding 
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

        print(encoding)
        if encoding == 'utf8':
            raise NotImplementedError('UTF-8 is not implemented yet')
        elif encoding == 'utf-16 le':
            # Parse the header and then the binary data
            lines = []
            sep = "\n"
            data_line = 'Binary:'
            with open(raw_path, 'rb') as file:
                buffer = ''
                while True:
                    next_bytes = file.read(2)
                    decoded = next_bytes.decode(encoding)
                    print(buffer)
                    if decoded == sep:
                        lines.append(buffer)
                        if buffer == data_line:
                            break
                        buffer = ''
                    else:
                        buffer += decoded
                return lines


                



if __name__=='__main__':
    netlist_path = 'ltspice_files/Lisn_sym_copy.net'
    ltrunner = LTSpiceRunner(netlist_path)
    # dd = pd.DataFrame({'Ts': [1/20e3, 1/30e3, 1/20e3, 1/30e3], 'dV': [0.1, 0.1, 0.8, 0.8]})
    dd = pd.DataFrame({'Ts': [1/20e3, 1/30e3], 'dV': [0.1, 0.8]})
    added = ltrunner.add_sweep(dd, 'Ry')
    if added:
        print("I am running the netlist")
        ltrunner._run(ascii=False)
        print("I finished simulating.")
        ltreader = LTSpiceReader(ltrunner)
        lines = ltreader._parse_raw()
        for line in lines:
            print(line)
        


