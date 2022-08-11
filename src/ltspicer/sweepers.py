import sys, os
from runners import PathFinder
import re 

class Sweeper:
    """Adds sweep to the LTSpice file."""
    pass

class NetlistCreator:
    """Creates the netlist from the ASC file."""
    @staticmethod
    def create(asc_file, ltspice_path=None):
        if sys.platform == 'win32':
            # Run a command to do it
            try:
                ltpath, _ = PathFinder.find_ltspice_path(ltspice_path)
                cmd = f"{ltpath} -netlist -b {asc_file}"
                A = subprocess.run(cmd, 
                            shell=True, check=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
                assert isinstance(A, subprocess.CompletedProcess) # Assert process has completed
                assert os.path.exists( re.sub(".asc", ".net", asc_file) ) # Assert netlist exists
                return True
            except Exception as e:
                raise e
        elif sys.platform == 'darwin':
            # From scratch
            pass
        else:
            raise NotImplementedError("Other systems are not implemented")

    def _create_mac(self, asc_file):
        # If only the asc file is given create the netlist by scanning the contents of asc file.
        pass


