import unittest 
import numpy as np
from ltspicer.readers import RawReader

class ReadersTest(unittest.TestCase):

    def test_empty_raw_reader(self):
        raw_reader = RawReader()
        self.assertIsNone(raw_reader.raw_path)

    def test_compute_step_indices(self):
        raw_reader = RawReader()
        raw_reader.header = {} # Create fake flags entry

        # Test non-stepped data
        raw_reader.header['Flags'] = ['complex']
        xvar = np.array([-1, 0.1, 0.3])
        stepdict = raw_reader._compute_step_indices(xvar)
        self.assertDictEqual(
            stepdict, {'step1': {'start': 0, 'n': 3}}
        )

        # Test stepped but with no flag
        xvar = np.concatenate([xvar, np.array([-1, 0.1, 0.3, -0.2, 0.3, 0.1, 0.3, 0.4, 1.5])])
        stepdict = raw_reader._compute_step_indices(xvar)
        benchdict = {
                "step1": {"start": 0, "n": 3},
                "step2": {"start": 3, "n": 3},
                "step3": {"start": 6, "n": 2},
                "step4": {"start": 8, "n": 4}
            }
        self.assertDictEqual(stepdict, {'step1': {'start': 0, 'n': 12}})

        # Test stepped with flag
        raw_reader.header['Flags'] = ['complex', 'stepped']
        stepdict = raw_reader._compute_step_indices(xvar)
        self.assertDictEqual(stepdict, benchdict)

    




if __name__=="__main__":
    unittest.main()

