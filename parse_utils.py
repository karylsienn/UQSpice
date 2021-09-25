
def parse_netlist(netlist_path):
    try:
        with open(netlist_path, 'r', encoding='utf-16 le') as file:
                lines = file.read().split('\n')
        file.close()
        return lines
    except FileNotFoundError:
        pass


def write_netlist(netlist_lines, netlist_path):
    try:
        with open(netlist_path, 'w', encoding='utf-16 le') as file:
            file.writelines("\n".join(netlist_lines))
        file.close()
    except Exception as e:
        print(e)