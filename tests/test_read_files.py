import os.path
import unittest
import pathlib
import numpy as np
import pandas as pd
from utils.read_files import read_las


class TestReadFiles(unittest.TestCase):
    def test_read_las(self):
        # Arrange
        path_to_input = 'test_data/test_las.las'
        path_to_this_file = pathlib.Path(__file__).parent.resolve()
        path_to_input = os.path.join(path_to_this_file, path_to_input)
        expected_DT_values = pd.Series(np.array([90.0, 89.9973, np.nan]))

        # Action
        actual_dataframe = read_las(path_to_input)
        actual_DT_values = actual_dataframe['DT']

        # Assertion
        for i, j in zip(expected_DT_values, actual_DT_values):
            if np.isnan(i) and np.isnan(j):
                self.assertTrue(True)
            else:
                self.assertEqual(i, j)


if __name__ == '__main__':
    unittest.main()
