from ltspice_runner import LTSpiceRunner
from datetime import datetime
import warnings
from parse_utils import ENC_UTF16LE, ENC_UTF8, parse_netlist, parse_log
import matplotlib.pyplot as plt
import re, mmap, os
import numpy as np
import pandas as pd


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
        # How many and what are the steps?
        # self.get_steps() 
        # Are there any meas or four commands?
        fullname = self.runner.get_fullname()
        netlist = parse_netlist(fullname)

        # Specify if there are any `meas` or `four` commands
        self.no_measurements = 0
        self.no_four = False
        for command in netlist:
            if re.match('.meas', command, re.IGNORECASE):
                self.no_measurements += 1
            elif re.match('.four', command, re.IGNORECASE):
                self.no_four +=1

    @staticmethod
    def _header_to_dict(headerlist, offset, encoding):
        assert type(headerlist) is list
        # For the variables columns make the binary stride
        header_dict = {}
        variables_idx = None
        for idx, line in enumerate(headerlist):
            searched = re.search(r'([A-Za-z\. ]+):(.*)$', line)
            key, value = searched.group(1).strip(), searched.group(2).strip()
            # Some values are numerical, such no. points, no. variables etc.
            if re.match(r'Offset', key, re.IGNORECASE):
                # Cast to number
                value = float(value)
            elif re.match(r'No. Variables|No. Points', key, re.IGNORECASE):
                # Cast to integer
                value = int(value)
            elif re.match(r'Date', key, re.IGNORECASE):
                # Create a datetime object
                value = datetime.strptime(value, "%a %b %d %H:%M:%S %Y")
            elif re.match(r'Flags', key, re.IGNORECASE):
                # Flags should be separated
                value = value.split(" ")
            elif re.match(r'^Variable', key, re.IGNORECASE):
                # The rest until `Data` flag should be the variable description
                variables_idx = idx+1
                break
            # Append the dictionary
            header_dict[key] = value

        if variables_idx is not None:
            # Variables should be the last thing before `Data` flag
            # and `Data` flag is the last thing in `header_lines`
            # `key` should be 'variables'
            header_dict[key] = pd.DataFrame([
                line.strip().split('\t')[1:] for line in headerlist[variables_idx:(len(headerlist)-1)]],
                columns=['Variable', 'Description'])
            header_dict["Binary_offset"] = offset # Append the number of lines at which "Data" or "Binary" appears
            header_dict["Encoding"] = encoding
        return header_dict

    def parse_header(self):
        filename = re.sub(r'.net$|.cir$|.asc$',r'.raw', self.runner.get_fullname())
        with open(filename, 'r+b') as rawfile:
            # Map the first part not to have to read it into the memory
            mm = mmap.mmap(rawfile.fileno(), 0)  # Map the whole file in place, not to run into memory issues
            
            # Check what is the enoding of the file
            title = mm.read(6)
            if title.decode(ENC_UTF8) == 'Title':
                encoding = ENC_UTF8
            elif title.decode(ENC_UTF16LE) == 'Tit':
                encoding = ENC_UTF16LE
            else:
                mm.close()
                raise ValueError(f"Unknown encoding of the file {filename}")

            # Find the binary part and get the results back
            # TODO: Implement ASCII.
            offset = mm.find("Binary:\n".encode(encoding))
            mm.close()

            # Create the header from the first part of the file
            headerlines = rawfile.read(offset)
            header = headerlines.decode(encoding).replace("\r", "\n").split("\n") # Useful for windows
            offset += 16 if encoding == ENC_UTF16LE else 8
            self.header = LTSpiceReader._header_to_dict(header, offset, encoding)
        

    def parse_rawfile(self):
        filename = re.sub(r'.net$|.cir$|.asc$',r'.raw', self.runner.get_fullname())
        offset = self.header["Binary_offset"]
        with open(filename, 'r+b') as rawfile:
            # Read the file from this offset onwards
            rawfile.seek(offset, os.SEEK_SET)
            binary = rawfile.read()

        # Get the binary in the simplest form possible
        binary = np.frombuffer(binary, dtype='uint8')

        # Get the number of points and variable for further file reading
        npoints, nvars = self.header['No. Points'], self.header['No. Variables']

        # What is the data type?
        if self._is_real():
            xnbytes, datanbytes = 8, 4
            xtype, datatype = "<f8", "<f4"
        elif self._is_complex():
            xnbytes = datanbytes = 16
            xtype = datatype = "<c16"
        else:
            raise ValueError("Uknown flags! Don't know how to read the raw file.")

        # TODO: Check if the length of the file is okay.
        # How many bytes are there per row of data?
        bytesperrow = xnbytes + (nvars-1)*datanbytes
        
        # We are setting the view using `as_strided`, which is generally not recommended
        xvar_uncompressed = np.lib.stride_tricks.as_strided(
            np.frombuffer(binary, dtype=xtype),
            shape=(npoints,),
            strides=(bytesperrow,))
        xvar = np.abs(xvar_uncompressed) # To prevent imposing abs on the rest of the data
        
        # Get the rest of the columns
        data = np.lib.stride_tricks.as_strided(
            np.frombuffer(binary[xnbytes:], dtype=datatype), # Read from the rest of the file
            shape=(npoints, nvars-1),
            strides=(bytesperrow, datanbytes))
        
        # Create a dictonary of steps or at least steps offsets
        if self._is_stepped():
            plotname = self.header['Plotname']
            try:
                self._step_indices = LTSpiceReader._get_step_indices(xvar, plotname)
            except Exception as e:
                print(e)
                warnings.warn("Making the step dictionary empty")
                self._step_indices = np.asarray([])
        else:
            self._step_indices = np.asarray([]) # Empty array

        # Have the data in self field
        self._data = data
        self._xvar = xvar


    @staticmethod
    def _get_step_indices(xvar, analysis_type):
        if re.match(r'transient|ac',analysis_type, re.IGNORECASE):
            # The value does not have to be the same for each step
            # The time vector should be monotically increasing, we will take the differences
            # and the index where the negative differences occur are the ones where the next step starts
            start_indices = np.insert(np.flatnonzero(np.diff(xvar) < 0) + 1, 0, 0)
            stop_indices = np.append(start_indices[1:]-1, len(xvar))
            sweeps = range(1, len(start_indices)+1)
            return pd.DataFrame({
                'step': sweeps,
                'start_idx': start_indices,
                'stop_idx': stop_indices
            }).set_index('step')  
        else:
            raise NotImplementedError("Other analyses are not implemented yet.")


    def parse_log(self):
        fullname = self.runner.get_fullname()
        log_path = re.sub(r'.net$|.asc$|.cir$', r'.log', fullname)
        self.log = parse_log(log_path)
        return self.log

    def get_measurements(self):
        # TODO: Put which measurements you want to read.
        start_idx, end_idx, dflist = 0, 0, []
        names = []
        found_meas, no_meas = False, 0
        for idx, line in enumerate(self.log):
            if re.match("Measurement", line):
                found_meas = True
                searched = re.search("Measurement:(.*)$", line)
                if searched:
                    name = searched.group(1).strip()
                    names.append(name)
            elif found_meas and re.search('step', line):
                # Line with names
                start_idx = idx
            elif found_meas and line == "":
                # Finished table
                end_idx = idx
                df = self._extract_meas_table(start_idx, end_idx)
                found_meas = False
                dflist.append(df)
                no_meas += 1
            elif not found_meas and no_meas == self.no_measurements:
                break
        
        dd = {name: df for name, df in zip(names, dflist)}
        self.dfmeas = dd
        return dd
      

    def measurements_to_df(self, measurements=None):
        if measurements is not None:
            chosen_meas = {new_key: self.dfmeas[new_key] for new_key in measurements}
        else:
            chosen_meas = self.dfmeas

        meas_fn = lambda m: m[m.columns.difference(['FROM', 'TO'])].set_index('step')
        meas = [meas_fn(meas) for meas in chosen_meas.values()]
        lastdf = meas[0]
        if len(meas) > 1:
            for m in meas[1:]:
                lastdf = lastdf.join(m)
        return lastdf

    def _extract_meas_table(self, start_idx, end_idx):
        df_lines = self.log[start_idx:end_idx]
        col_header = [x.strip() for x in df_lines[0].split("\t")]
        col_types = ['int', 'float', 'float', 'float']
        dtype = list(zip(col_header, col_types))
        fl = lambda x: self.__find_float(x)
        arr = np.array([tuple(fl(y.strip()) for y in x.split("\t")) for x in df_lines[1:]],
                dtype=dtype)
        return pd.DataFrame.from_records(arr)

    def get_four(self):
        # TODO: make fourier dictionary - maybe the user doesn't want to read everything?
        dflist, step, four_past = [], 0, 0
        for idx, line in enumerate(self.log):
            if re.match(".step", line):
                step += 1
            elif re.match("Fourier components of ", line):
                searched = re.search("Fourier components of (.*)$", line)
                node = searched.group(1).strip()
            elif re.match("N-Period", line):
                searched = re.search("N-Period=([0-9]+)", line)
                period = int(searched.group(1).strip())
            elif re.match("DC component", line):
                searched = re.search("DC component:(.*)$", line)
                dc_component = float(searched.group(1).strip())
            elif re.match("Harmonic\tFrequency", line):
                start_idx = idx
            elif re.match("Total Harmonic Distortion", line):
                four_past += 1
                # put end_idx and extract the THD
                end_idx = idx
                df = self._extract_four_df(start_idx, end_idx)
                searched = re.search("Total Harmonic Distortion: (.*)\%\((.*)\%\)", line)
                thd1 = float(searched.group(1))
                thd2 = float(searched.group(2))

                # Append the table on exit
                df['node'] = node
                df['no. periods'] = period
                df['dc'] = dc_component
                df["thd1"] = thd1/1e2
                df["thd2"] = thd2/1e2
                df["step"] = step 

                if four_past <= self.no_four:
                    dflist.append(df)
                    four_past = 0
        
        df = pd.concat(dflist)
        self.dffour = df
        return df
                

    def _extract_four_df(self, start_idx, end_idx):
        df_lines = self.log[start_idx:end_idx]
        col_headers = df_lines[:2]
        col_headers = [x.split("\t") for x in col_headers]
        col_headers = [" ".join([x.strip(), y.strip()]) for x, y in zip(col_headers[0], col_headers[1]) ]
        col_types = ["int", "float","float", "float", "float", "float"]
        dtype = list(zip(col_headers, col_types))
        fl = lambda x: self.__find_float(x)
        arr = np.array([tuple(fl(y.strip()) for y in x.split("\t")) for x in df_lines[2:]],
                dtype=dtype)
        return pd.DataFrame.from_records(arr)

    @staticmethod
    def __find_float(x):
        searched = re.search(r"[-+]?(\d+([.,]\d*)?|[.,]\d+)([eE][-+]?\d+)?", x)
        if searched:
            return(searched.group(1))
        else:
            raise ValueError("There is no float here.")

    def get_steps(self, num_only=False):
        """
        Creates a dictionary of steps with appropriate information
        """
        if self.log is None:
            self.parse_log()
        # Filter lines with .step command
        step_lines = [line for line in self.log if re.match('^.step', line, re.IGNORECASE)]
        no_steps = len(step_lines)
        self.no_steps = no_steps
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

    def _is_stepped(self):
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
    print("LTSpice Reader")