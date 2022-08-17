import sys, os
import warnings
from ltspicer.pathfinder import LTPathFinder
from ltspicer.readers import NetlistReader
import re 
import subprocess
from random import random
import pandas as pd
from typing import List

ENC_UTF16LE = 'utf-16 le'
ENC_UTF8 = 'utf8'


class Sweeper:
    """Adds sweep to the LTSpice netlist."""
    def __init__(self):
        self.hash = hash(random())
        self.enter_line = f"* Sweep added by Sweeper {self.hash}"
        self.exit_line = f'* Finished sweep by Sweeper {self.hash}'

    def __hash__(self):
        return self.hash

    @staticmethod
    def _create_sweep_command(input_samples: pd.DataFrame, sweep_param_name):
        """
        Creates the sweep command based on the rows of the `input_samples`
        """
        nrows = len(input_samples)

        # First line .step command
        nsamples_str = " ".join([str(x + 1) for x in range(nrows)])
        param_line = f".step param {sweep_param_name} list {nsamples_str}"

        # lambda for pasting the index with the value with a comma
        values_fn = lambda inpt: ','.join(
            str(idx) + ',' + str(val)
            for idx, val in zip(range(1, nrows + 1), inpt))

        # Parameters command for the sweep
        values_lines = [
            f".param {col} table({sweep_param_name}, {values_fn(input_samples[col])})"
            for col in input_samples]

        return param_line, values_lines

    def add_sweep(self, netlist_path: str, input_samples: pd.DataFrame, sweep_param_name='Rx'):
        """
        Appends the netlist with sweep command created from the `input_samples`.
        """
        param, values = self._create_sweep_command(input_samples, sweep_param_name)
        # Read the netlist
        try:
            netlist = NetlistReader.read(netlist_path)  # Hard encoding now.
        except FileNotFoundError or UnicodeDecodeError as e:
            raise e

        # Add this before the .backanno command
        for idx, command in enumerate(netlist):
            if re.match('.backanno', command):
                netlist.insert(idx, self.enter_line)
                netlist.insert(idx + 1, param)
                end_idx = idx + 2
                for idy, value in enumerate(values):
                    netlist.insert(idx + idy + 2, value)
                    end_idx = idx + idy + 3
                netlist.insert(end_idx, self.exit_line)
                break
        try:
            NetlistCreator.write_netlist_lines(netlist, netlist_path)
            return True
        except Exception as e:
            raise e

    def clean_sweeps(self, netlist_path: str):
        try:
            netlist = NetlistReader.read(netlist_path)
        except UnicodeDecodeError or FileNotFoundError as e:
            raise e

        en = enumerate(netlist)
        for idx, command in en:
            if re.match(re.escape(self.enter_line), command):
                start_idx = idx
            elif re.match(re.escape(self.exit_line), command):
                end_idx = idx
                break
            else:
                pass

        while start_idx <= end_idx:
            netlist.pop(start_idx)
            end_idx -= 1

        try:
            NetlistCreator.write_netlist_lines(netlist, netlist_path)
            return True
        except Exception as e:
            raise e


class NetlistCreator:
    """Creates the netlist from the ASC file."""
    @staticmethod
    def create(asc_file, ltspice_path=None):
        ltpath = LTPathFinder.find_exe_ltspice_path(ltspice_path)
        timeout = 20
        pre, ext = os.path.splitext(asc_file)
        asc_file = '"' + asc_file + '"'
        if sys.platform in ('win32', 'linux'):
            if sys.platform == 'win32':
                cmd = f'"{ltpath}" -netlist {asc_file}'
            else:
                cmd = f"wine {ltpath} -netlist {asc_file}"
            # Run a command to do it
            try:            
                A = subprocess.run(cmd, 
                                   shell=True, check=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
                assert isinstance(A, subprocess.CompletedProcess) # Assert process has completed
                assert os.path.exists(pre + '.net')  # Assert netlist exists
                return True
            except Exception as e:
                raise e
        elif sys.platform == 'darwin':
            # From scratch
            pass
        else:
            raise NotImplementedError("Other systems are not implemented")

    def _create_mac(self, asc_file):
        # TODO
        # If only the asc file is given create the netlist by scanning the contents of asc file.
        pass

    @staticmethod
    def write_netlist_lines(netlist_lines: List[str], netlist_path: str):
        # First check encoding
        if os.path.exists(netlist_path):
            warnings.warn("Updating existing netlist.")
            encoding = NetlistReader.guess_encoding(netlist_path)
        else:
            warnings.warn("Creating new netlist")
            if sys.platform in ('win32', 'linux'):
                encoding = ENC_UTF8
            elif sys.platform == 'darwin':
                encoding = ENC_UTF16LE
            else:
                raise NotImplementedError("Platforms other than Mac, Windows and Linux (wine) are not implemented yet.")

        try:
            netlist_lines = [line + '\n' for line in netlist_lines]
            for elements in range(len(netlist_lines)):
                if '�' in netlist_lines[elements]:
                    netlist_lines[elements] = netlist_lines[elements].replace('�', 'u')

            with open(netlist_path, 'w', encoding=encoding) as netlist:
                netlist.writelines(netlist_lines)
            netlist.close()
            return True
        except Exception as e:
            raise e




