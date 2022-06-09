from distutils.log import warn
from select import select
import unittest 
import numpy as np
import warnings, os

from sympy import N
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

class HeaderParserTransientTests(unittest.TestCase):
    
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.raw_reader = RawReader()
        self.test_files_path = "test_files"
        self.raw_reader.raw_path = os.path.join(self.test_files_path, "Transient", "simple_resistor.raw")
        self.raw_reader._parse_header() 

    def test_header_keys(self):
        header = self.raw_reader.header
        hkeys = header.keys()
        for k in ("Title", "Date", "Plotname", "Flags", "No. Variables", "No. Points", "Command", "Variables", "Binary_offset", "Encoding"):
            self.assertIn(k, hkeys)
    
    def test_encoding_is_correct(self):
        self.assertEqual(self.raw_reader.header['Encoding'], 'utf-16 le')
    
    def test_flags(self):
        for flag in self.raw_reader.header['Flags']:
            self.assertIn(flag, ("real", "forward"))
            self.assertNotIn(flag, ("complex", "stepped"))

    def test_is_not_stepped(self):
        self.assertFalse(self.raw_reader._is_stepped())
    
    def test_is_real_and_not_complex(self):
        self.assertTrue(self.raw_reader._is_real())
        self.assertFalse(self.raw_reader._is_complex())
        
    def test_no_points_is_correct(self):
        self.assertEqual(self.raw_reader.header["No. Points"], 4)

    def test_no_variables_is_correct(self):
        self.assertEqual(self.raw_reader.header['No. Variables'], 4)
    
    def test_variable_names(self):
        header_variables = self.raw_reader.header['Variables']
        variables = {
            "time": {"Index": 0, "Description": "time"},
            "V(n001)": {"Index": 1, "Description": "voltage"},
            "I(R1)": {"Index": 2, "Description": "device_current"},
            "I(V1)": {"Index": 3, "Description": "device_current"}
        }
        self.assertDictEqual(header_variables, variables)

class RawParserTransientTests(unittest.TestCase):

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.raw_reader = RawReader()
        self.test_files_path = "test_files"
        self.raw_reader.raw_path = os.path.join(self.test_files_path, "Transient", "simple_resistor.raw")
        self.raw_reader._parse_header() 
        self.raw_reader._parse_rawfile()
    
    def test_step_dict_matches(self):
        stepdict = self.raw_reader.get_steps('all')
        self.assertDictEqual(
            stepdict,
            {'step1': {'start': 0, 'n': 4}}
        )
        self.assertEqual(
            self.raw_reader.header["No. Points"],
            stepdict['step1']['n']
        )
    
    def test_check_get_selected_columns_all(self):
        columns = self.raw_reader._check_get_selected_columns(selection='all')
        self.assertEqual(
            columns, [
                ("V(n001)", 0), ("I(R1)", 1), ("I(V1)", 2)]
        )
    
    def test_check_get_selected_columns_raises_value_error_when_empty_selection(self):
        with self.assertRaises(ValueError):
            self.raw_reader._check_get_selected_columns(selection=[]) # Empty selection
    
    def test_check_get_selected_columns_raises_value_error_when_wrong_selection(self):
        with self.assertRaises(ValueError):
            self.raw_reader._check_get_selected_columns(selection=['V(n002)', 'I(V2)'])
    
    def test_check_get_selected_columns_returns_selected_column(self):
        selected_col = self.raw_reader._check_get_selected_columns(selection=['I(R1)'])
        self.assertEqual(selected_col, [("I(R1)", 1)])

    def test_check_get_selected_columns_returns_selected_columns(self):
        selected_cols = self.raw_reader._check_get_selected_columns(selection=['I(R1)', 'V(n001)'])
        self.assertEqual(selected_cols, [ ("V(n001)", 0), ("I(R1)", 1) ])
    
    def test_check_get_selected_columns_warns_about_nonexistent_columns(self):
        with warnings.catch_warnings(record=True) as w:
            selected_cols = self.raw_reader._check_get_selected_columns(selection=['I(R1)', 'I(R11)', 'I(R12)'])
            self.assertEqual(selected_cols, [('I(R1)', 1)])
            self.assertEqual(
                str(w[-1].message), 
                "Columns: I(R11),I(R12) are not present in the data. Proceeding with the remaining columns.")
    
    """
    Non-interpolated versions of the non-stepped data.
    """
    def test_get_data_array_returns_empty_data_when_nonexistent_steps_and_warns_about_it(self):
        with warnings.catch_warnings(record=True) as w:
            x, d, s = self.raw_reader._get_data_array(columns='all', steps=[2, 3], interpolated=False)
            self.assertEqual(len(x), 0)
            self.assertEqual(len(d), 0)
            self.assertEqual(len(s), 0)
            self.assertIsInstance(w[-1], warnings.WarningMessage)
    
    def test_get_data_array_returns_full_original_data_by_default(self):
        x, d, s = self.raw_reader._get_data_array()
        self.assertEqual(len(x), self.raw_reader.header['No. Points'])
        self.assertEqual(d.shape, (self.raw_reader.header['No. Points'], self.raw_reader.header['No. Variables']-1))
        self.assertListEqual(list(s), [1,1,1,1]) and isinstance(s, np.array)

    def test_get_data_contents_are_the_same_in_ltspice(self):
        pass

if __name__=="__main__":
    unittest.main()

