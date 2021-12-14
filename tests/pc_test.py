import polynomial_chaos as pc
import unittest

class TestPC(unittest.TestCase):

    def test_get_exerimental_design(self):
        variables_dict = {
            "X1": {
                "distribution": "normal",
                "parameters": {
                    "mu": 432,
                    "var": 10
                }
            },
            "X2": {
                "distribution": "uniform",
                "parameters": {
                    "min": 10,
                    "max": 20
                }
            }
        }

        N = 20

        pcarchitect = pc.PCArchitect(variables_dict)
        experimental_design = pcarchitect.get_experimental_design(N, dataframe_only=True)
        print(experimental_design)
        return True

    def test_dummy(self):
        pass



if __name__=='__main__':
    unittest.main()