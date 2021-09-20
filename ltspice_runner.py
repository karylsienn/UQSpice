import os, subprocess, sys, re


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
        pass


