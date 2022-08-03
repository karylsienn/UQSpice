from posixpath import basename
import sys
import os
import subprocess

class LTSpiceRunner:
    """
    LTSpiceRunner is an interface to the executable of LTSpice.
    It can run the .asc, .net or other suitable LTSpice file.

    In the initialization, one can provide the path to LTSpice executable.
    Otherwise the path is searched for. Currently only macOS and Windows executables are supported.

    """
    def __init__(self, ltspice_path=None) -> None:
        if ltspice_path and os.path.exists(ltspice_path)\
            and os.access(ltspice_path, os.X_OK):
            self._ltspice = ltspice_path
            if sys.platform == 'darwin':
                self._cmd_separator = '; '
            elif sys.platform == 'win32':
                self._cmd_separator = ' && '
            else:
                raise NotImplementedError("Platforms other than Mac and Windows are not implemented yet")
        else:
            try: 
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

    def create_netlist(self):
        # TODO: Create a Netlist from a schematic file. Asc file cannot be run from command line on macOS.
        
        pass

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
        
        


