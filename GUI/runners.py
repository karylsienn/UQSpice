from posixpath import basename
import sys
import os
import subprocess

class PathFinder:
    """Finds and returns LTSpice path if not provided by the user."""
    @staticmethod
    def find_ltspice_path(ltspice_path=None):
        if ltspice_path and os.path.exists(ltspice_path)\
            and os.access(ltspice_path, os.X_OK): # Check if it is an executable.
            ltpath = ltspice_path
            if sys.platform == 'darwin':
                cmd_sep = '; '
            elif sys.platform == 'win32':
                cmd_sep = ' && '
            else:
                raise NotImplementedError("Platforms other than Mac and Windows are not implemented yet")
        else:
            try: 
                if sys.platform == 'darwin':
                    ltpath = "/Applications/LTspice.app/Contents/MacOS/LTspice"
                    cmd_sep = "; "
                elif sys.platform == 'win32':
                    ltpath = '"C:\\Program Files\\LTC\\LTspiceXVII\\XVIIx64.exe"'
                    cmd_sep = " && "
                else:
                    ltpath = None
                    raise NotImplementedError("Platforms other than Mac and Windows are not implemented yet")
            except Exception as e:
                raise e
        
        return ltpath, cmd_sep


class LTSpiceRunner:
    """
    LTSpiceRunner is an interface to the executable of LTSpice.
    It can run the .asc, .net or other suitable LTSpice file.

    In the initialization, one can provide the path to LTSpice executable.
    Otherwise the path is searched for. Currently only macOS and Windows executables are supported.

    """
    def __init__(self, ltspice_path=None) -> None:
        self._ltspice_path, self._cmd_separator = PathFinder.find_ltspice_path(ltspice_path)


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
        
        


