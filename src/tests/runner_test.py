import unittest
from ltspicer.runners import LTSpiceRunner

class RunTests(unittest.TestCase):

    def test_running_asc(self):
        ltrunner = LTSpiceRunner()
        self.assertTrue(ltrunner.run("test_files/Transient/simple_resistor_ver2.asc"))
