from io import UnsupportedOperation
import re, os
from datetime import datetime
from numpy import exp
import pandas as pd
from struct import unpack


ENC_UTF16LE = 'utf-16-le'
ENC_UTF8 = 'utf8'

DTYPE_FLOAT64 = 'float64'
DTYPE_COMPLEX128 = 'complex128'

def parse_netlist(netlist_path, encoding=None):
    if os.path.exists(netlist_path):
        if encoding is None:
            try:
                with open(netlist_path, 'r', encoding=ENC_UTF8) as file:
                    line = file.readline()
                    encoding = ENC_UTF8
                file.close()

            except Exception as e:
                try:
                    with open(netlist_path, 'r', encoding=ENC_UTF16LE) as file:
                        line = file.readline()
                        encoding = ENC_UTF16LE
                    file.close()
                
                except Exception as e:
                    raise e

        elif encoding is not None:
            encoding = check_encoding(encoding)

        if encoding is not None:
            try:
                with open(netlist_path, 'r', encoding=encoding) as file:
                    lines = file.read().split('\n')
                file.close()
                return lines
            except Exception as e:
                raise e  
    else:
        raise FileNotFoundError(f"Couldn't find file {netlist_path}.")
        


def write_netlist(netlist_lines, netlist_path, encoding=None):
    if encoding is None:
        print(f"Unspecified encoding, using {ENC_UTF16LE}.")
        encoding = ENC_UTF16LE
    try:
        with open(netlist_path, 'w', encoding=encoding) as file:
            file.writelines("\n".join(netlist_lines))
        file.close()
    except Exception as e:
        print(e)



def parse_log(log_path, encoding=None):
    if os.path.exists(log_path):
        # Guess encoding
        if encoding is None:
            with open(log_path, 'rb') as file:
                first_bytes = file.read(8)
                if first_bytes.decode(ENC_UTF8) == 'Circuit:':
                    encoding = ENC_UTF8
                elif first_bytes.decode(ENC_UTF16LE) == 'Circ':
                    encoding = ENC_UTF16LE
                else:
                    raise UnicodeEncodeError(f'Uknown encoding of the log file {log_path}')
            file.close()

        if encoding is not None and file.closed:
            try:
                with open(log_path, 'r', encoding=encoding) as file:
                    lines = file.read().split('\n')
                file.close()
                return lines
            except Exception as e:
                raise e
    else:
        raise FileNotFoundError(f"Couldn't find file {log_path}.")


def parse_binary(raw_path, no_points, no_variables,
                index_start=None, col_idx=None, col_names=None,
                dtype=DTYPE_FLOAT64, header_encoding=ENC_UTF8):

    if index_start is None or index_start <= 0:
        raise ValueError("Index start should be defined and greater than zero.")
    
    # The error has not been raised, move forward.
    if col_idx is None or any(cidx < 0 for cidx in col_idx):
        # By default read all variables
        col_idx == range(no_variables)
    
    # Check `col_names`
    if col_names is None:
        # Provide the names for the variables if not specified
        col_names = ["X"+str(i) for i in len(col_idx)]
    elif type(col_names) is list:
        if len(col_idx) != len(col_names):
            raise ValueError("Lengths of `col_idx` and `col_names` do not match.")
        else:
            # Make sure the names of the variables are strings
            col_names = [str(cnm) for cnm in col_names]
    elif type(col_names) is not list:
        if len(col_idx) > 1:
            raise ValueError("The lengths of `col_names` and `col_idx` do not match.")
        col_names = str(col_names) 

    try:
        dtype = check_datatype(dtype)
        header_encoding = check_encoding(header_encoding)
    except Exception as e:
        raise e

    with open(raw_path, 'rb') as file:
        decodedfun = read_byte_utf16le if header_encoding == ENC_UTF16LE else read_byte_utf8
        sep, data_line, no_lines = "\n", "Binary:\n", 1
        # Pass the header until you reach the binary part 
        while no_lines < index_start:
            decoded = decodedfun(file)
            if decoded == sep:
                no_lines += 1
        # Confirm that this line is the same as the `data_line`
        buffer = "".join(decodedfun(file) for _ in range(len(data_line)))
        if buffer != data_line:
            raise ValueError(f"I can't find the appropriate flag '{data_line}'. Are you sure `index_start` is correct?")

        # Create a dictionary with col_idx and col_names
        col_dict = {cidx: cnm for cidx, cnm in zip(col_idx, col_names)}
        data_df = pd.DataFrame({
            name: range(no_points) for name in col_names},
            dtype=dtype)
        
        readfun = read_real4 if dtype==DTYPE_FLOAT64 else read_complex16
        for i in range(int(no_points)):
            for var_idx in range(no_variables):
                # Read variable by variable
                if (var_idx in col_idx):
                    # Get the name of this columns
                    name = col_dict[var_idx]
                    if var_idx==0:
                        # Read the time or frequency
                        data_df.at[i, name] = read_real8(file)
                    else:
                        # Read the variables provided in columns
                        data_df.at[i, name] = readfun(file)
                else:
                    readfun(file) # Just read and pass.
        
    file.close()
    return data_df
                

    
def parse_data(fullname, index_start=None, columns=None, add_step_info=True, dtype='float64'):
    raise NotImplementedError("This function is not implemented yet.")


def parse_header(raw_path, encoding=None):
    if encoding is not None:
        encoding = check_encoding(encoding)
    # raw_path = re.sub(r'.asc$|.cir$|.net$', '.raw', fullname)
    with open(raw_path, 'rb') as file:
        # If the encoding has not been provided guess it.
        first_6_bytes = None
        if encoding is None:
            # Guess encoding
            first_6_bytes = file.read(6)
            if first_6_bytes.decode(ENC_UTF8) == 'Title:':
                encoding = ENC_UTF8
            elif first_6_bytes.decode(ENC_UTF16LE) == 'Tit':
                encoding = ENC_UTF16LE
            else:
                raise Exception("Couldn't find correct encoding.")

        # If encoding is known read further
        decodedfun = read_byte_utf16le if encoding == ENC_UTF16LE else read_byte_utf8
        lines, sep, binary_line, data_line, no_lines = [], "\n", "Binary:", "Data:", 1
        buffer = first_6_bytes.decode(encoding) if first_6_bytes is not None else ''
        # TODO: What happens when Data line is not found? Prevent infinite loop.
        while True:
            decoded = decodedfun(file)
            if decoded == sep:
                lines.append(buffer)
                no_lines +=1 # How many lines to read if we don't want to read.
                if (buffer in [data_line, binary_line]):
                    break
                buffer = ''
            else:
                buffer += decoded
        
            # Create the dictionary containing the header elements.
            header_dict = {}
            variables_idx = None
            for idx, line in enumerate(lines):
                searched = re.search(r'([A-Za-z\. ]+):(.*)$', line)
                key, value = searched.group(1).strip(), searched.group(2).strip()
                # Some values are numerical, such no. points, no. variables etc.
                if re.match(r'No. Variables|No. Points|Offset', key, re.IGNORECASE):
                    # Cast to number
                    value = float(value)
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
                    line.strip().split('\t')[1:] for line in lines[variables_idx:(len(lines)-1)]],
                    columns=['Variable', 'Description'])
                header_dict["No. Lines"] = no_lines # Append the number of lines at which "Data" or "Binary" appears
                header_dict["Data flag"] = buffer # Last buffer should have the data flag
                header_dict["Encoding"] = encoding

    file.close()
    return header_dict if len(header_dict) > 0 else None


def read_byte_utf8(file):
    return file.read(1).decode(ENC_UTF8)

def read_byte_utf16le(file):
    return file.read(2).decode(ENC_UTF16LE)

def read_real4(file):
    """
    Read the real data saved in 4 bytes.
    """
    return unpack('f', file.read(4))[0]

def read_real8(file):
    """
    Read the timestamp or the frequency, saved as 8 bytes.
    """
    return unpack('d', file.read(8))[0]

def read_complex16(file):
    """
    Read the complex data, saved in two 8-bytes chunks (for real and imaginary parts)
    """
    (real, imaginary) = unpack('dd', file.read(16))
    return complex(real=real, imag=imaginary)


def check_encoding(encoding):
    if re.match(r"UTF( |-){0,1}16( |-){0,1}LE", encoding.upper()):
        return ENC_UTF16LE
    elif re.match(r"UTF( |-){0,1}8", encoding.upper()):
        return ENC_UTF8
    else:
        raise ValueError(f"Not supported encoding. The only supported ones are {ENC_UTF8} and {ENC_UTF16LE}")


def check_datatype(dtype):
    if dtype=='float64':
        return DTYPE_FLOAT64
    elif dtype == 'complex128':
        return DTYPE_COMPLEX128
    else:
        raise ValueError(f"Not supported data type. The only supported ones are {DTYPE_FLOAT64} and {DTYPE_COMPLEX128}.")
