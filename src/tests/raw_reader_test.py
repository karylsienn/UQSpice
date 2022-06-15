from distutils.log import warn
from logging import warning
from select import select
import unittest 
import numpy as np
import warnings, os

from sympy import N, interpolate
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
        self.raw_reader.raw_path = os.path.join(self.test_files_path, "Transient", "simple_resistor_copy.raw")
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
        self.raw_reader.raw_path = os.path.join(self.test_files_path, "Transient", "simple_resistor_copy.raw")
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
        self.assertEqual(selected_cols, [ ("I(R1)", 1), ("V(n001)", 0)  ])
    
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
            x, d, s, _ = self.raw_reader._get_data_array(columns='all', steps=[2, 3], interpolated=False)
            self.assertEqual(len(x), 0)
            self.assertEqual(len(d), 0)
            self.assertEqual(len(s), 0)
            self.assertIsInstance(w[-1], warnings.WarningMessage)
    
    def test_get_data_array_returns_full_original_data_by_default(self):
        x, d, s, _ = self.raw_reader._get_data_array()
        self.assertEqual(len(x), self.raw_reader.header['No. Points'])
        self.assertEqual(d.shape, (self.raw_reader.header['No. Points'], self.raw_reader.header['No. Variables']-1))
        self.assertListEqual(list(s), [1,1,1,1]) and isinstance(s, np.array)

    def test_get_data_returns_correct_selected_data(self):
        x, d, _, _ = self.raw_reader._get_data_array(columns=['I(R1)', 'I(V1)'])
        self.assertTrue(np.all(np.diff(x) > 0)) # Monotonic x
        self.assertTrue(np.all(d[:, 0] > 1.2))
        self.assertTrue(np.all(d[:, 1] < -1.2))
    

class RawParserTransientSteppedTests(unittest.TestCase):

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.raw_reader = RawReader()
        self.test_files_path = "test_files"
        self.raw_reader.raw_path = os.path.join(self.test_files_path, "Transient", "simple_resistor_stepped_copy.raw") # 3 steps 1, 2, 5
        self.raw_reader._parse_header() 
        self.raw_reader._parse_rawfile()
    
    def test_get_data_array_returns_all_data(self):
        x, d, s, _= self.raw_reader._get_data_array()
        self.assertTrue(len(x), self.raw_reader.header['No. Points'])
        self.assertTrue(d.shape, (self.raw_reader.header['No. Points'], self.raw_reader.header['No. Variables']-1))
        self.assertListEqual(list(s), [1,1,1,1,2,2,2,2,3,3,3,3])

    def test_get_data_array_returns_monotonic_steps(self):
        x, _, _, _= self.raw_reader._get_data_array()
        for i in range(3):
            self.assertTrue( np.all(np.diff(x[i*4:((i+1)*4)])) ) # Check the times are monotonic.
        self.assertLess(x[4], x[3]) and self.assertLess(x[8], x[7])   # And that between steps there are gaps

    def test_get_data_array_returns_steps_in_correct_order(self):
        _, d, _, _ = self.raw_reader._get_data_array(columns=['I(R1)'])
        eps = 1e-9
        voltage = 4
        resistances = [1, 2, 5]
        for i, r in enumerate(resistances):
            ltspice_i = d[(i*4):((i+1)*4), 0]
            self.assertLess( np.max(np.abs(ltspice_i*r-voltage)), eps)
    
    def test_get_data_array_returns_selected_steps(self):
        _, d, _, _ = self.raw_reader._get_data_array(columns='I(R1)', steps=[2])
        v, r, eps = 4, 2, 1e-9
        self.assertEqual(d.shape, (4, 1))
        self.assertLess( np.max(np.abs(d*r-v)), eps )

class AnalysisTypeTests(unittest.TestCase):

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.ac_reader = RawReader("test_files/AC/simple_rlc_copy.raw")
        self.tran_reader = RawReader("test_files/Transient/simple_resistor_stepped_copy.raw")
    
    def test_ac_analysis_type(self):
        self.assertEqual(self.ac_reader.get_analysis_type(), 'ac')
    
    def test_transient_analysis_type(self):
        self.assertEqual(self.tran_reader.get_analysis_type(), 'transient')

    def test_ac_flags(self):
        self.assertTrue(self.ac_reader._is_complex()) and self.assertFalse(self.ac_reader._is_real())
    
    def test_tran_flags(self):
        self.assertTrue(self.tran_reader._is_real()) and self.assertFalse(self.tran_reader._is_complex())

class InterpolatedDataTests(unittest.TestCase):

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.tran_reader = RawReader("test_files/Transient/simple_resistor_stepped_copy.raw")
        self.ac_reader =  RawReader("test_files/AC/simple_rlc_copy.raw")
    
    def test_defaults(self):
        x, d, s, _ = self.tran_reader._get_data_array(interpolated=True)
        xorig, dorig, sorig, _ = self.tran_reader._get_data_array(interpolated=False)
        self.assertEqual(d.shape, (12, 3))
        self.assertEqual(x.shape, (12, ))
        self.assertListEqual(list(s), list(np.repeat([1,2,3], 4)))
        for i in range(3):
            self.assertListEqual(list(d[:, i]), list(dorig[:,i])) # they are constant so should be the same
        
    def test_kwargs(self):
        x, d, _, _ = self.tran_reader._get_data_array(interpolated=True, n=8, tmin=0.0008, tmax=0.0012)
        self.assertEqual(x.shape, (8*3,))
        self.assertEqual(d.shape, (8*3, 3))
        for i in [0, 8, 16]:
            self.assertAlmostEqual(x[i], 0.0008)
            self.assertAlmostEqual(x[i+7], 0.0012)
    
    def test_steps_and_columns_selection(self):
        x, d, s, _ = self.tran_reader._get_data_array(steps=[1,3], columns=['I(R1)', 'V(n001)'],
                                                    interpolated=True, n=6)
        self.assertEqual(x.shape, (12,))
        self.assertEqual(d.shape, (12, 2))
        self.assertEqual(list(s), [1]*6 + [3]*6)

    def test_raises_error_when_analysis_not_transient(self):
        with self.assertRaises(NotImplementedError):
            self.ac_reader._get_data_array(interpolated=True)
        

class PandasAndNumpyTests(unittest.TestCase):

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.tran_reader = RawReader("test_files/Transient/simple_resistor_stepped_copy.raw")
        self.ac_reader = RawReader("test_files/AC/simple_rlc_copy.raw")
    
    def test_pandas_transient_interpolated_df(self):
        df = self.tran_reader.get_pandas(steps=[1,2], columns=['I(R1)', 'V(n001)'],
                                        interpolated=True, n=3)
        self.assertListEqual(list(df.columns), ['time', 'step', 'I(R1)', 'V(n001)'])
        self.assertEqual(df.shape, (6, 4))
    
    def test_pandas_ac_interpolated_df_raises_error(self):
        with self.assertRaises(NotImplementedError):
            self.ac_reader.get_pandas(interpolated=True)

    def test_pandas_ac_df(self):
        df = self.ac_reader.get_pandas(steps=[1,2], columns=['I(R1)', 'V(n001)'])
        self.assertEqual(df.shape, (2*19, 4))
    
    def test_numpy_and_pandas_are_the_same(self):
        df = self.ac_reader.get_pandas(steps=[1,2], columns=['I(R1)', 'V(n001)'])
        arr = self.ac_reader.get_numpy(steps=[1,2], columns=['I(R1)', 'V(n001)'])
        self.assertTrue(np.all(arr == np.asarray(df)))


if __name__=="__main__":
    unittest.main()

