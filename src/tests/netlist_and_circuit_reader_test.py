import unittest
from ltspicer.readers import NetlistReader, CircuitReader

class NetlistReaderTests(unittest.TestCase):

    def test_reading_utf16le(self):
        netlist = NetlistReader.read_netlist("test_files/Transient/netlist_creation_copy.net")
        self.assertEqual(len(netlist), 11) # Since the last line is a blank line


class CircuitReaderTests(unittest.TestCase):

    def test_reading_utf16le(self):
        circuit = CircuitReader.read_circuit("test_files/Transient/netlist_creation.asc")
        self.assertEqual(len(circuit), 46)
