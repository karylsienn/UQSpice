from posixpath import basename
import sys
import os
import subprocess
from pathfinder import LTPathFinder

class LTSpiceRunner:
    """
    LTSpiceRunner is an interface to the executable of LTSpice.
    It can run the .asc, .net or other suitable LTSpice file.

    In the initialization, one can provide the path to LTSpice executable.
    Otherwise the path is searched for. Currently only macOS and Windows executables are supported.

    """
    def __init__(self, ltspice_path=None) -> None:
        self._ltspice_path  = LTPathFinder.find_exe_ltspice_path(ltspice_path)
        self._cmd_separator = LTPathFinder.find_cmd_sep()


    def run(self, file_to_run, ascii=False, timeout=20):
        dirname, basename = os.path.dirname(file_to_run), os.path.basename(file_to_run)
        try:
            if self._ltspice is not None:
                cmd =  self._cmd_separator.join([
                    f"cd {dirname if len(dirname) > 0 else '.'}",
                    f"{self._ltspice} {'-ascii' if ascii else ''} -b {basename}"])
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
        
        


