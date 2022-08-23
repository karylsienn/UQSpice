import argparse
import mmap
import os
import re
import warnings
from datetime import datetime
from typing import List, Tuple

import numpy as np
import pandas as pd

ENC_UTF16LE = 'utf-16 le'
ENC_UTF8 = 'utf8'


def complex_to_re_im(column: pd.Series) -> pd.DataFrame:
    """
    Cast complex column to its real and imaginary part.
    Example usage:

    `df = raw_reader.get_pandas()`

    `complex_to_re_im(df['V(n003)'])`

    Parameters
    ----------
    * column : pandas.Series
            the complex column to extract real and imaginary parts

    Returns
    -------
    pandas.DataFrame
        a dataframe with two columns containing real and imaginary parts

    """
    column_name = column.name
    return pd.DataFrame({
        "Re(" + column_name + ")": np.real(column),
        "Im(" + column_name + ")": np.imag(column)
    })


def complex_to_abs_rad(column: pd.Series) -> pd.DataFrame:
    column_name = column.name
    return pd.DataFrame({
        "Abs(" + column_name + ")": np.abs(column),
        "Rad(" + column_name + ")": np.angle(column, deg=False)
    })


def complex_to_log10_deg(column: pd.Series) -> pd.DataFrame:
    column_name = column.name
    return pd.DataFrame({
        "Abs(" + column_name + ")": np.log10(np.abs(column)),
        "Deg(" + column_name + ")": np.angle(column, deg=True)
    })


class InputReader:
    @staticmethod
    def read(path: str):
        pass

    @staticmethod
    def guess_encoding(path: str):
        pass


class NetlistReader(InputReader):
    """Reads the netlist file and returns its content as a list of strings"""

    @staticmethod
    def read(netlist_path: str) -> List[str]:
        # Assert the file exists.
        if os.path.exists(netlist_path):
            # Parse the file and return a list of strings
            try:
                encoding = NetlistReader.guess_encoding(netlist_path)
            except UnicodeDecodeError as e:
                raise e

            with open(netlist_path, 'r', encoding=encoding, errors='replace') as netlist:
                netlist_lines = netlist.readlines()
                netlist_lines = [line.strip("\r\n") for line in netlist_lines]
            netlist.close()
            return netlist_lines

        else:
            raise FileNotFoundError("There was a problem reading your file.")

    @staticmethod
    def guess_encoding(netlist_path: str) -> str:
        with open(netlist_path, 'rb') as netlist:
            # Guess the encoding
            first_bytes = netlist.read(2)
            if first_bytes.decode(ENC_UTF16LE) == '*':
                encoding = ENC_UTF16LE
            elif first_bytes.decode(ENC_UTF8)[0] == '*':
                encoding = ENC_UTF8
            else:
                raise UnicodeDecodeError(
                    f"Unknown encoding. "
                    f"Make sure the files are either in {ENC_UTF16LE} or {ENC_UTF8}")
        netlist.close()
        return encoding


class CircuitReader(InputReader):
    """Reads the circuit file and returns its content as a list of strings"""

    @staticmethod
    def read(circuit_path: str) -> List[str]:
        # Assert the file exists.
        if os.path.exists(circuit_path):
            # Parse the file and return a list of strings
            try:
                encoding = CircuitReader.guess_encoding(circuit_path)
            except UnicodeDecodeError as e:
                raise e

            with open(circuit_path, 'r', encoding=encoding, errors='replace') as circuit:
                circuit_lines = circuit.readlines()
                circuit_lines = [line.strip("\r\n") for line in circuit_lines]
            circuit.close()
            return circuit_lines

        else:
            raise FileNotFoundError("There was a problem reading your file.")

    @staticmethod
    def guess_encoding(circuit_path):
        with open(circuit_path, 'rb') as netlist:
            # Guess the encoding
            first_bytes = netlist.read(6)
            if first_bytes.decode(ENC_UTF16LE) == 'Ver':
                encoding = ENC_UTF16LE
            elif first_bytes.decode(ENC_UTF8) == 'Versio':
                encoding = ENC_UTF8
            else:
                raise UnicodeDecodeError(
                    f"Unknown encoding. Make sure the files are either in {ENC_UTF16LE} or {ENC_UTF8}")
        netlist.close()
        return encoding


class LTSpiceReader:
    """Base class for the output readers (raw and log files)"""
    pass


class RawReader(LTSpiceReader):
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
        else:  # For unit testing purposes
            self.raw_path = None

    def get_pandas(self,
                   columns: Tuple[str] | str = 'all',
                   steps: Tuple[int] | int | str = 'all',
                   interpolated: bool = False,
                   **kwargs) -> pd.DataFrame:
        """Returns a copy of the raw data as `pandas.DataFrame`.

        Parameter `columns` can be either a list of column names or 'all'.
        `steps` can be a list, numpy array, an integer or 'all'. If the data is stepped
        only a required portion of the data will be returned and a column `step` added 
        to a data frame. In case the required steps are not in the data, a warning will
        be shown and only existing steps will be returned, or an empty data frame in case
        `steps` do not match any existing steps.

        For .tran analysis interpolation may be required. If `interpolated` is set to `True`
        the returned data frame will be interpolated for evenly-spaced points. The interpolation
        parameters can be set as keyword arguments. By default, a minimal time span across all steps
        is taken and maximum number of points is computed.
        
        Parameters
        ----------
        columns : list or str (default is "all")
            names of columns 
        steps : list | integer | str (default "all")
            steps of the LTspice analysis 
        interpolated : boolean (default False)
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

        Returns
        -------
        pandas.DataFrame
            a copy of the LTSpice data

        Raises
        -------
        NotImplementedError
            if an interpolation is performed for data coming from not transient (.tran) analysis


        """
        try:
            xvar, data, stepnp, colnames = self._get_data_array(columns,
                                                                steps,
                                                                interpolated,
                                                                **kwargs)
            xname = 'time' if self.get_analysis_type() == 'transient' else 'frequency'
            df = pd.DataFrame(
                np.hstack((xvar.reshape((-1, 1)), stepnp.reshape((-1, 1)), data)),
                columns=[xname, 'step'] + list(colnames))
            if df[xname].dtype == 'complex':  # AC analysis
                df[xname] = np.real(df[xname])  # Cast frequency to float
                df['step'] = np.real(df['step']).astype(int)  # Cast `step` to integer
            else:  # A transient analysis.
                df['step'] = df['step'].astype(int)  # Cast step to integer
            return df
        except NotImplementedError as e:
            raise e

    def get_numpy(self, columns='all', steps='all', interpolated=False, **kwargs):
        """Returns a copy of the raw data as `numpy.array`.

        Parameter `columns` can be either a tuple of column names or 'all'.
        `steps` can be a list, numpy array, an integer or 'all'. If the data is stepped
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
        interpolated : boolean (default False)
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

        Returns
        -------
        numpy.array
            a copy of the LTSpice data

        Raises
        -------
        NotImplementedError
            if an interpolation is performed for data coming from not transient (.tran) analysis


        """
        try:
            xvar, data, stepnp, _ = self._get_data_array(columns, steps, interpolated, **kwargs)
            return np.hstack((xvar.reshape((-1, 1)), stepnp.reshape((-1, 1)), data))
        except NotImplementedError as e:
            raise e

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

    def get_analysis_type(self):
        """Returns the analysis type of this RawReader instance.        

        The possible values are 'transient' and 'ac'.

        Raises:
        -------
        NotImplementedError
            if the raw file consists analyses other than ac and transient.
        """
        plotname = self.header['Plotname']
        if re.match('transient', plotname, re.IGNORECASE):
            return 'transient'
        elif re.match('ac', plotname, re.IGNORECASE):
            return 'ac'
        else:
            return NotImplementedError("Other analyses are not yet implemented")

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
        bytesperrow = xnbytes + (nvars - 1) * datanbytes
        endbyte = len(binary)
        while endbyte % xnbytes != 0:
            endbyte -= 1

        # We are setting the view using `as_strided`, which is generally not recommended
        xvar_uncompressed = np.lib.stride_tricks.as_strided(  # Thanks to Pete Lonsdale.
            np.frombuffer(binary[:endbyte], dtype=xtype),
            shape=(npoints,),
            strides=(bytesperrow,))

        xvar = np.abs(xvar_uncompressed)  # To prevent imposing abs on the rest of the data

        # Get the rest of the columns
        data = np.lib.stride_tricks.as_strided(
            np.frombuffer(binary[xnbytes:], dtype=datatype),  # Read from the rest of the file
            shape=(npoints, nvars - 1),
            strides=(bytesperrow, datanbytes))

        # Append the data in self field
        self._step_indices = self._compute_step_indices(xvar)  # Create a dictonary of steps or at least steps offsets
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
            header = headerlines.decode(encoding).replace("\r", "\n").split("\n")  # Useful for windows
            offset += 16 if encoding == ENC_UTF16LE else 8
            self.header = RawReader._header_to_dict(header, offset, encoding)

    def _compute_step_indices(self, xvar):
        if self._is_stepped():
            start_indices = np.insert(np.flatnonzero(np.diff(xvar) < 0) + 1, 0, 0)
            lengths = np.append(start_indices[1:], len(xvar)) - start_indices
            steps = range(1, len(start_indices) + 1)
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

    @staticmethod
    def _steps_dict_to_numpy_array(steps_dict):
        reps = [(
            int(re.match('step([0-9]+)', k).group(1)),  # take the step number
            v['n']  # compute the number of repetitions
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
            searched = re.search(r'([A-Za-z. ]+):(.*)$', line)
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
                variables_idx = idx + 1
                break
            # Append the dictionary
            header_dict[key] = value

        if variables_idx is not None:
            # Variables should be the last thing before `Data` flag
            # and `Data` flag is the last thing in `header_lines`
            # `key` should be 'variables'
            header_dict[key] = {}
            for i, line in enumerate(headerlist[variables_idx:(len(headerlist) - 1)]):
                ls = line.strip().split('\t')[1:]
                colname = ls[0]
                header_dict[key][colname] = {
                    'Index': i,
                    'Description': ls[1]
                }
            header_dict["Binary_offset"] = offset  # Append the number of lines at which "Data" or "Binary" appears
            header_dict["Encoding"] = encoding
        return header_dict

    def _get_data_array(self, columns='all', steps='all', interpolated=False, **kwargs):
        try:  # First get the columns
            cols = self._check_get_selected_columns(selection=columns)
            cols, idxs = list(zip(*cols))
        except ValueError as e:
            raise e

        try:  # Get the steps
            step_dict = self._check_get_selected_steps(steps)
        except ValueError as e:
            warnings.warn("%s Returning empty array.".format(str(e)))
            return np.array([]), np.array([]), np.array([]), cols

        if len(cols) == len(self._get_all_column_names()) \
                and len(step_dict) == len(self._get_all_steps()) and not interpolated:
            # Return a copy of the whole data 
            return self._xvar.copy(), self._data.copy(), self._steps_dict_to_numpy_array(step_dict), cols

        if not interpolated:
            arrlist, xvar = [], np.array([], dtype=self._xvar.dtype)
            for _, sv in step_dict.items():
                start, numpoints = sv['start'], sv['n']
                arrpart = self._data[start:(start + numpoints), idxs].copy()
                arrpart = arrpart.reshape((numpoints), len(cols))
                arrlist.append(arrpart)
                xvar = np.concatenate([xvar, self._xvar[start:(start + numpoints)].copy()])
            return xvar, np.concatenate(arrlist), self._steps_dict_to_numpy_array(step_dict), cols
        else:
            if self.get_analysis_type() != 'transient':
                raise NotImplementedError("Only linear interpolation provided. "
                                          "Recommended to use only with transient analysis.")

            defaults = {  # Default values if keywords are not present
                'n': max([v['n'] for v in step_dict.values()]),
                'tmin': max([self._xvar[v['start']] for v in step_dict.values()]),
                'tmax': min([self._xvar[v['start'] + v['n'] - 1] for v in step_dict.values()])
            }
            n = kwargs.get("n", defaults['n'])
            tmin = kwargs.get("tmin", defaults['tmin'])
            tmax = kwargs.get("tmax", defaults['tmax'])
            # Preallocate the array for holding the interpolated version of the data.
            nsteps, ncol = len(step_dict), len(cols)
            tt = np.linspace(tmin, tmax, n, dtype=self._data.dtype)
            interp_xvar = np.tile(tt, nsteps)
            interp_data = np.zeros(shape=(nsteps * n, ncol), dtype=self._data.dtype)
            for i, v in enumerate(step_dict.values()):
                # apply along rows axis-0 - returns new array so can be used with strided view
                stepidx = slice(v['start'], v['start'] + v['n'])
                interp_data[slice(i * n, (i + 1) * n), idxs] = np.apply_along_axis(
                    func1d=lambda y: np.interp(tt, self._xvar[stepidx], y), \
                    axis=0, arr=self._data[stepidx, idxs])
            return interp_xvar, interp_data, self._steps_dict_to_numpy_array({
                k: {'start': i * n, 'n': n} for i, k in enumerate(step_dict.keys())
            }), cols

    def _check_get_selected_columns(self, selection):
        # Sort columns names with respect to the index -- get rid of the first name
        available_columns = sorted([(k, v['Index'] - 1) for k, v in self.header['Variables'].items()],
                                   key=lambda x: x[1])
        _ = available_columns.pop(0)  # pop x-axis column
        if isinstance(selection, str) and re.match('all', selection, re.IGNORECASE):
            return available_columns

        if type(selection) is str:
            selection = [selection]

        unknown_cols = []  # Check selected columns exist in the data.
        acolnms = [acol for acol, _ in available_columns]
        n = len(selection)
        for _ in range(n):
            if selection[-1] not in acolnms:
                unknown_cols.append(selection.pop())

        if len(selection) == 0:  # Is there anything left?
            raise ValueError("No columns could be selected.")

        if len(unknown_cols) > 0:
            warnings.warn(
                f"Columns: {','.join(reversed(unknown_cols)) if len(unknown_cols) > 1 else unknown_cols[0]} are not present in the data. Proceeding with the remaining columns.")
        # All checks passed - iterate through `available_columns` to return sorted version.
        # Update: return columns in the order of appearance
        available_columns_dict = {col: idx for col, idx in available_columns}
        return [(col, available_columns_dict[col]) for col in selection]

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
                warnings.warn(
                    f"Steps: {','.join([str(u) for u in unselected]) if len(unselected) > 1 else unselected[0]} are not present in the dataset and will be omitted")
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
        return any(re.match('complex', line, re.IGNORECASE) for line in self.header['Flags'])


class LogReader(LTSpiceReader):

    def __init__(self, log_path) -> None:
        self.log_path = log_path


class MeasurementReader(LogReader):

    def __init__(self, log_path) -> None:
        self.super().__init__(log_path)

    def get_pandas(self):
        pass


class FourierAnalysisReader(LogReader):

    def __init__(self, log_path) -> None:
        self.super().__init__(log_path)

    def get_pandas(self):
        pass


def parse_and_save(
        objstr: str,
        infile: str,
        outfile: str,
        **kwargs):
    """The main function. Reads the file and saves the results to a csv file."""

    if objstr == "RawReader" and re.search(r"\.raw$", infile):

        # Create an instance of a reader
        reader = RawReader(infile)

        # Parse the keyword arguments
        columns = kwargs.get("columns", 'all')
        steps = kwargs.get("steps", 'all')
        interpolated = kwargs.get("interpolated", False)
        rest = {k: v for k, v in kwargs.items() if k not in ('columns', 'steps', 'interpolated')}

        # Get the resulting dataframe.
        data = reader.get_pandas(columns=columns, steps=steps, interpolated=interpolated, **rest)

        # Store the dataframe in a file
        if len(outfile) == 0:
            outfile = re.sub(".raw", ".csv", infile)
        data.to_csv(outfile, index=False)
        print("Saved.")

    elif objstr == "MeasurementReader" and re.search(r"\.log$", infile):
        pass
    elif objstr == "FourierAnalysisReader" and re.search(r"\.log$", infile):
        pass
    else:
        raise ValueError("""Reader must be one of: RawReader, MeasurementReader, FourierAnalysisReader.
                            Make sure that the .log and .raw files match the reader.""")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Read a file using the LTSpiceReader and return pandas or numpy.")
    # TODO: Maybe it will be better with subcommands?
    # subparsers = parser.add_subparsers()
    # parser_raw = subparsers.add_parser(name="raw", help="Read the raw file using RawReader")

    parser.add_argument("-r", "--reader",
                        required=True,
                        type=str,
                        choices=("RawReader", "MeasurementReader", "FourierAnalysisReader"),
                        help="""A name of the class to read the file. 
                        This should be either RawReader, MeasurementReader or FourierAnalysisReader.""")
    parser.add_argument("-f", "--file",
                        required=True,
                        type=str,
                        help="The file you want to read.")
    parser.add_argument("-o", "--outfile",
                        required=False,
                        type=str,
                        help="Output file where to store the results",
                        default="")

    # Group for numpy or pandas -- Maybe not really needed.
    # group = parser.add_mutually_exclusive_group(required=True)
    # group.add_argument("--numpy", "-np", action="store_true")
    # group.add_argument("--pandas", "-pd", action="store_true")

    # Further arguments for RawReader
    raw_group = parser.add_argument_group("Raw")
    raw_group.add_argument("--columns", "-col",
                           required=False,
                           nargs='*',
                           default='all')
    raw_group.add_argument("--steps", "-s",
                           required=False,
                           nargs="*",
                           default='all')
    raw_group.add_argument("--interpolated", "-i",
                           required=False,
                           action='store_true')
    raw_group.add_argument("--tmin",
                           required=False,
                           type=float)
    raw_group.add_argument("--tmax",
                           required=False,
                           type=float)
    raw_group.add_argument("--n",
                           required=False,
                           type=int)

    # Parse the arguments
    args = parser.parse_args()

    # Get the main arguments
    objstr = args.reader
    infile = args.file
    outfile = args.outfile
    # result = 'pandas' if args.pandas else 'numpy'
    rest = {k: v for k, v in args._get_kwargs() if k not in ('reader', 'file', 'outfile', 'numpy', 'pandas')}

    # Run the main function
    parse_and_save(
        objstr=objstr,
        infile=infile,
        outfile=outfile,
        **rest)
