import sys, os
from ltspicer.pathfinder import LTPathFinder
import re 
import subprocess

class Sweeper:
    """Adds sweep to the LTSpice file."""
    pass

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
                cmd = f"wine {ltpath} -b -netlist {asc_file}"
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


