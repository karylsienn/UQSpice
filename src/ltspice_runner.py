import os, subprocess, sys, re
import pandas as pd
from parse_utils import parse_netlist, write_netlist
import re
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

    def add_sweep(self, input_samples: pd.DataFrame, sweep_param_name='Rx', encoding=None):
        """
        Appends the netlist with sweep command created from the `input_samples`.
        """
        param, values = self._create_sweep_command(input_samples, sweep_param_name)
        # Read the netlist
        netlist = parse_netlist(self.get_fullname(), encoding=encoding) # Hard encoding now.

        # Add this before the .backanno command
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
            

    def _save_cols(self, cols=None):
        # It is reasonable to save only selected variables to both speed-up the simulation
        # and the postprocessing of the data
        # TODO: implement
        pass



    def run(self, timeout=20, ascii=False, cols=None):

        # Save a portion of the columns.
        if cols is not None:
            self._save_cols(cols)
        
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
    
                

if __name__=='__main__':
    print("LTSpiceRunner.")


