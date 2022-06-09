from distutils.log import warn
import unittest 
import numpy as np
import warnings
from ltspicer.readers import RawReader

class StepDictTests(unittest.TestCase):

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.raw_reader = RawReader()

    def test_empty_raw_reader(self):
        self.assertIsNone(self.raw_reader.raw_path)

    def test_compute_step_indices(self):
        raw_reader = self.raw_reader
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
    
    def test_step_dict_to_numpy_array(self):
        stepsdict = {
            'step1': {'start': 0, 'n': 2},
            'step2': {'start': 2, 'n': 8},
            'step3': {'start': 10, 'n': 1}
        }
        benchmark = np.array([1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3])
        computed = self.raw_reader._steps_dict_to_numpy_array(stepsdict)
        self.assertListEqual(list(benchmark), list(computed))

    def test_step_dict_to_numpy_array_1step(self):
        computed = self.raw_reader._steps_dict_to_numpy_array({"step1": {"start": 0, "n": 4}})
        benchmark = np.array([1, 1, 1, 1])
        self.assertListEqual(list(computed), list(benchmark))


class GetStepsTests(unittest.TestCase):

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.raw_reader = RawReader()
        self.raw_reader.header = {}
        self.raw_reader.header['Flags'] = ['stepped']
        stepsdict = self.raw_reader._compute_step_indices(np.array([-1, 0.1, 0.3, -0.2, 0.3, 0.1, 0.3, 0.4, 1.5]))
        self.raw_reader._step_indices = stepsdict

    def test_get_steps_throws_value_error_with_no_valid_steps(self):
        with self.assertRaises(ValueError):
            self.raw_reader.get_steps(steps=[4,5,6])
    
    def test_get_steps_throws_value_error_with_str_no_all(self):
        with self.assertRaises(ValueError):
            self.raw_reader.get_steps(steps='sth')
    
    def test_get_steps_returns_original_dict_with_all(self):
        self.assertDictEqual(
            {
                "step1": {"start": 0, "n": 3},
                "step2": {"start": 3, "n": 2},
                "step3": {"start": 5, "n": 4}
            },
            self.raw_reader.get_steps(steps='all')
        )
    
    def test_get_steps_returns_original_dict_with_steps(self):
        self.assertDictEqual(
            self.raw_reader.get_steps(steps='all'),
            self.raw_reader.get_steps(steps=[1,2,3])
        )

    def test_get_steps_warns_with_nonpresent_steps(self):
        with warnings.catch_warnings(record=True) as w:
            self.assertDictEqual(
                self.raw_reader.get_steps(steps='all'),
                self.raw_reader.get_steps(steps=[0,1,2,3,4,5])
            )
            self.assertEqual(
                str(w[-1].message),
                "Steps: 0,4,5 are not present in the dataset and will be omitted"
            )

if __name__=="__main__":
    unittest.main()

