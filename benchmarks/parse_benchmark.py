
ENC_UTF8 = 'utf8'
ENC_UTF16LE = 'utf-16-le'

def parse_binary1(raw_path, no_points, no_variables,
                index_start=None, col_idx=None, col_names=None,
                dtype='float64', header_encoding=ENC_UTF8):
    pass


def parse_binary2(raw_path, no_points, no_variables,
                index_start=None, col_idx=None, col_names=None,
                dtype='float64', header_encoding=ENC_UTF8):
    
    with open(raw_path, 'rb') as file:
        sep, data_line, no_lines = "\n", "Binary", 1
        while no_lines < index_start:
            decoded = file.read(1).decode(header_encoding)
            if decoded == sep:
                no_lines +=1
        buffer = "".join(file.read(1).decode(header_encoding) for _ in range(len(data_line)))
        if buffer != data_line:
            raise ValueError(f"I can't find the appropriate flag '{data_line}'")



if __name__=="__main__":
    
    path = "../ltspice_files/raport03/Lisn_sym_meas.raw"
    index_start = 34 # the start index counts from 1, not from zero.
    header_encoding = ENC_UTF16LE
    no_variables = 22
    no_points = 1093445
    dtype = 'float64'



