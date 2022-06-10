from logging import warning
from multiprocessing.sharedctypes import Value
from matplotlib.pyplot import plot
import numpy as np
import re, mmap, warnings, os
from datetime import datetime

ENC_UTF16LE = 'utf-16 le'
ENC_UTF8 = 'utf8'


class RawReader:
    """RawReader parses the raw LTSpice file given in 'raw_path'.

    It implements three methods for returning the data:
        * get_pandas
        * get_numpy
        * get_steps
    The first two methods return a copy of the parsed raw data
    as `pandas.DataFrame` or `numpy.array`.
    The latter method returns a dictionary
        {
            'step1': {
                'start': start_idx, 
                'n': length
            },
            'step2': {
                'start': start_idx, 
                'n': length
            },
            
            ...

            'stepn': {
                'start': start_idx,
                'n': length
            }
        }
    of the original stepped data (if the data is stepped). 

    In case the LTSpice raw file consists results of transient analysis,
    the data can be interpolated, such that it consists evenly-spaced data points. 
    """

    def __init__(self, raw_path=None) -> None:
        if raw_path:
            self.raw_path = raw_path
            # TODO: maybe find operating point.
            self._parse_header()
            self._parse_rawfile()
        else: # For unit testing purposes
            self.raw_path = None

    def get_pandas(self, columns='all', steps='all', interpolated=True, **kwargs):
        """Returns a copy of the raw data as `pandas.DataFrame`.

        Parameter `columns` can be either a list of column names or 'all'.
        `steps` can be a list, numpy.array, an integer or 'all'. If the data is stepped 
        only a required portion of the data will be returned and a column `step` added 
        to a data frame. In case the required steps are not in the data, a warning will
        be shown and only existing steps will be returned, or an empty data frame in case
        `steps` do not match any existing steps.

        For .tran analysis interpolation may be required. If `interpolated` is set to `True`
        the returned data frame will be interpolated for evenly-spaced points. The interpolation
        parameters can be set as keyword arguments. By default a minimal time span across all steps
        is taken and maximum number of points is computed.
        
        Parameters
        ----------
        columns : list or str (default is "all")
            names of columns 
        steps : list | integer | str (default "all")
            steps of the LTspice analysis 
        interpolated : boolean (default True)
            whether to interpolate the data (only used when analysis is .tran)
        **kwargs
            Additional keyword arguments passed to interpolation, see below
        
        Other Parameters
        ----------------
        tmin : float
            smallest time instant (start) for performing interpolation
        tmax : float
            largest time instant (stop) for performing interpolation
        n : int
            number of evenly-spaced time instants

        """
        import pandas as pd
        # TODO: Return in order of selection
        pass

    def get_numpy(self, columns='all', steps='all', interpolated=True, **kwargs):
        pass

    def get_steps(self, steps='all'):
        """Returns the dictionary
        {
            'step1': {
                'start': start_idx, 
                'n': length
            },
            'step2': {
                'start': start_idx, 
                'n': length
            },
            
            ...

            'stepn': {
                'start': start_idx,
                'n': length
            }
        }
        of steps of the original LTSpice simulation.
        
        Parameters:
        ------------
        steps : list or str (default 'all')
            the steps of the LTSpice simulation
        """
        return self._check_get_selected_steps(steps).copy()


    def _parse_rawfile(self):
        offset = self.header["Binary_offset"]
        with open(self.raw_path, 'r+b') as rawfile:
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
        endbyte = len(binary)
        while endbyte % xnbytes != 0:
            endbyte -= 1

        # We are setting the view using `as_strided`, which is generally not recommended
        xvar_uncompressed = np.lib.stride_tricks.as_strided( # Thanks to Pete Lonsdale.
            np.frombuffer(binary[:endbyte], dtype=xtype),
            shape=(npoints,),
            strides=(bytesperrow,))
        
        xvar = np.abs(xvar_uncompressed) # To prevent imposing abs on the rest of the data
        
        # Get the rest of the columns
        data = np.lib.stride_tricks.as_strided(
            np.frombuffer(binary[xnbytes:], dtype=datatype), # Read from the rest of the file
            shape=(npoints, nvars-1),
            strides=(bytesperrow, datanbytes))
        
        # Append the data in self field
        self._step_indices = self._compute_step_indices(xvar) # Create a dictonary of steps or at least steps offsets
        self._data = data
        self._xvar = xvar

    def _parse_header(self) -> None:
        with open(self.raw_path, 'r+b') as rawfile:
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
                raise ValueError(f"Unknown encoding of the file {self.raw_path}")
            # Find the binary part and get the results back
            # TODO: Implement ASCII.
            offset = mm.find("Binary:\n".encode(encoding))
            mm.close()
            # Create the header from the first part of the file
            headerlines = rawfile.read(offset)
            header = headerlines.decode(encoding).replace("\r", "\n").split("\n") # Useful for windows
            offset += 16 if encoding == ENC_UTF16LE else 8
            self.header = RawReader._header_to_dict(header, offset, encoding)

    def _compute_step_indices(self, xvar):
        if self._is_stepped():
            start_indices = np.insert(np.flatnonzero(np.diff(xvar) < 0) + 1, 0, 0)
            lengths = np.append(start_indices[1:], len(xvar)) - start_indices
            steps = range(1, len(start_indices)+1)
            return {
                f"step{step}": {
                    'start': start_indices[i],
                    'n': lengths[i]
                } for i, step in enumerate(steps)
            }
        else:
            return {
                "step1": {
                    "start": 0,
                    "n": len(xvar)
                }
            }
    
    def _steps_dict_to_numpy_array(self, steps_dict):
        reps = [(
            int(re.match('step([0-9]+)', k).group(1)), # take the step number
            v['n'] # compute the number of repetitions
        ) for k, v in steps_dict.items()]
        reps = list(zip(*reps))
        return np.repeat(reps[0], reps[1])

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
            header_dict[key] = {}
            for i, line in enumerate(headerlist[variables_idx:(len(headerlist)-1)]):
                ls = line.strip().split('\t')[1:]
                colname = ls[0]
                header_dict[key][colname] = {
                    'Index': i,
                    'Description': ls[1]
                }
            header_dict["Binary_offset"] = offset # Append the number of lines at which "Data" or "Binary" appears
            header_dict["Encoding"] = encoding
        return header_dict


    def _get_data_array(self, columns='all', steps='all', interpolated=False, **kwargs):
        try: # First get the columns
            cols = self._check_get_selected_columns(selection=columns)
            cols, idxs = list(zip(*cols))
        except ValueError as e:
            raise e

        try: # Get the steps
            step_dict = self._check_get_selected_steps(steps)
        except ValueError as e:
            warnings.warn("%s Returning empty array.".format(str(e)))
            return np.array([]), np.array([]), np.array([])
        
        if len(cols) == len(self._get_all_column_names()) and len(step_dict) == len(self._get_all_steps()):
            # Return a copy of the whole data 
            return self._xvar.copy(), self._data.copy(), self._steps_dict_to_numpy_array(step_dict)

        if not interpolated:
            arrlist, xvar = [], np.array([], dtype=self._xvar.dtype)
            for _, sv in step_dict.items():
                start, numpoints = sv['start'], sv['n']
                arrpart = self._data[start:(start+numpoints), idxs].copy()
                arrpart = arrpart.reshape((numpoints), len(cols))
                arrlist.append(arrpart)
                xvar = np.concatenate([xvar, self._xvar[start:(start+numpoints)].copy()])
            return xvar, np.concatenate(arrlist), self._steps_dict_to_numpy_array(step_dict)
        else:
            # TODO
            pass


    def _check_get_selected_columns(self, selection):
        # Sort columns names with respect to the index -- get rid of the first name
        available_columns = sorted([(k, v['Index']-1) for k, v in self.header['Variables'].items()],
                                   key=lambda x: x[1])
        _ = available_columns.pop(0) # pop x-axis column
        if isinstance(selection, str) and re.match('all', selection, re.IGNORECASE):
            return available_columns    

        if type(selection) is str: 
            selection = [selection] 

        unknown_cols = [] # Check selected columns exist in the data.
        acolnms = [acol for acol, _ in available_columns]
        n = len(selection)
        for _ in range(n):
            if selection[-1] not in acolnms:
                unknown_cols.append(selection.pop())
        
        if len(selection) == 0: # Is there anything left?
            raise ValueError("No columns could be selected.")

        if len(unknown_cols) > 0:
            warnings.warn(f"Columns: {','.join(reversed(unknown_cols)) if len(unknown_cols) > 1 else unknown_cols[0]} are not present in the data. Proceeding with the remaining columns.")
        # All checks passed - iterate through `available_columns` to return sorted version.
        return [(col, idx) for col, idx in available_columns if col in selection]


    def _check_get_selected_steps(self, selection): 
        # Quietly assuming (for now) that we have either string or list-like flat object
        if isinstance(selection, str) and re.match('all', selection, re.IGNORECASE):
            return self._step_indices.copy() 
        elif isinstance(selection, str):
            raise ValueError("`selection` can be 'all' or a list of ints")
        else:
            assert isinstance(selection[0], int)
            unselected, selected = [], {}
            for s in selection:
                key = f"step{int(s)}"
                if key in self._step_indices.keys():
                    selected[key] = self._step_indices[key]
                else:
                    unselected.append(s)
            if len(unselected) > 0:
                warnings.warn(f"Steps: {','.join([str(u) for u in unselected]) if len(unselected) > 1 else unselected[0]} are not present in the dataset and will be omitted")
            if len(selected) == 0:
                raise ValueError("There are no valid steps in the data!")
            return selected

    def _get_all_column_names(self):
        return list(self.header['Variables'].keys())[1:]
    
    def _get_xname(self):
        return list(self.header['Variables'].keys())[0]

    def _get_all_steps(self):
        return list(self._step_indices.keys())

    """
    Several checks mostly going through Flags in the header.
    """
    def _is_stepped(self):
        return any(re.match('stepped', line, re.IGNORECASE) for line in self.header['Flags'])

    def _is_real(self):
        return any(re.match('real', line, re.IGNORECASE) for line in self.header['Flags'])

    def _is_complex(self):
        return any(re.match('complex', line, re.IGNORECASE ) for line in self.header['Flags'])

    def get_analysis_type(self):
        plotname = self.header['Plotname']
        if re.match('transient', plotname, re.IGNORECASE):
            return 'transient'
        elif re.match('ac', plotname, re.IGNORECASE):
            return 'ac'
        else:
            return NotImplementedError("Other analyses are not yet implemented")


class LogReader:

    def __init__(self, log_path) -> None:
        self.log_path = log_path

