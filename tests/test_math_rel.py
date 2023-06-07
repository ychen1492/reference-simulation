import unittest

import numpy as np

from utils.math_rel import harmonic_average, arithmetic_average


class TestReadFiles(unittest.TestCase):
    def test_harmonic_average_with_correct_input_and_upscaling_amount(self):
        # Arrange
        test_input_array = np.array([0.2, 0.1, 1, 0.5, 0.5])
        test_upscaling_amount = 2
        expected_groups = [0.1875, 0.5]
        # Action
        actual_groups = harmonic_average(test_input_array, test_upscaling_amount)
        # Assert
        np.testing.assert_almost_equal(expected_groups, actual_groups, 8)

    def test_arithmatic_average_with_correct_input_and_upscaling_amount(self):
        # Arrange
        test_input_array = np.array([0.2, 0.6, 1, 0.5, 0.5])
        test_upscaling_amount = 2
        expected_groups = [0.6, 0.5]
        # Action
        actual_groups = arithmetic_average(test_input_array, test_upscaling_amount)
        # Assert
        np.testing.assert_almost_equal(expected_groups, actual_groups, 8)

    def test_harmonic_average_throw_exception(self):
        # Arrange
        test_input_array = np.array([0.2, 0.1, 1, 0.5, 0.5])
        test_upscaling_amount = 10
        # Assert
        with self.assertRaises(ValueError) as context:
            harmonic_average(test_input_array, test_upscaling_amount)
            self.assertEqual('Can not upscale the input, please check upscaled amount...', str(context.exception))

    def test_arithmatic_average_throw_exception(self):
        # Arrange
        test_input_array = np.array([0.2, 0.1, 1, 0.5, 0.5])
        test_upscaling_amount = 10
        # Assert
        with self.assertRaises(ValueError) as context:
            arithmetic_average(test_input_array, test_upscaling_amount)
            self.assertEqual('Can not upscale the input, please check upscaled amount...', str(context.exception))


if __name__ == '__main__':
    unittest.main()
