import unittest
from unittest.mock import patch, mock_open
from pathlib import Path
from pyrorb.experiments.base_experiment import BaseExperiment 
from pyrorb.utils import make_par


class TestBaseExperiment(unittest.TestCase):

    @patch('pyrorb.experiments.base_experiment.open', new_callable=mock_open, read_data='mock data')
    @patch('pyrorb.experiments.base_experiment.make_par', return_value='mock par data')
    def test_initialization(self, mock_make_par, mock_open):
        # Mock file paths
        catg_path = 'test.catg'
        stm_path = 'test.stm'

        # Create BaseExperiment instance
        experiment = BaseExperiment(catg_path, stm_path)

        # Check if files were read
        mock_open.assert_any_call(catg_path, 'r', encoding='ISO-8859-1')
        mock_open.assert_any_call(stm_path, 'r', encoding='ISO-8859-1')

        # Check if data is read correctly
        self.assertEqual(experiment.catg_data, 'mock data')
        self.assertEqual(experiment.stm_data, 'mock data')

        # Check default parameters
        self.assertEqual(experiment.parameters.kc, 0.4)
        self.assertEqual(experiment.parameters.m, 1.2)
        self.assertEqual(experiment.parameters.il, 10.0)
        self.assertEqual(experiment.parameters.cl, 5.0)

    @patch('pyrorb.experiments.base_experiment.open', new_callable=mock_open)
    def test_write_files(self, mock_open):
        catg_path = 'test.catg'
        stm_path = 'test.stm'
        output_path = 'output_dir'

        experiment = BaseExperiment(catg_path, stm_path)

        experiment.write_files(output_path)

        # Check if the write method was called correctly
        mock_open.assert_any_call(Path(output_path) / experiment._par_temporary_file_name, 'w')
        mock_open.assert_any_call(Path(output_path) / experiment._catg_temporary_file_name, 'w')
        mock_open.assert_any_call(Path(output_path) / experiment._stm_temporary_file_name, 'w')

    @patch('pyrorb.experiments.base_experiment.open', new_callable=mock_open, read_data='mock data')
    @patch('pyrorb.experiments.base_experiment.make_par', return_value='mock par data')
    def test_par_data(self, mock_make_par, mock_open):
        catg_path = 'test.catg'
        stm_path = 'test.stm'

        experiment = BaseExperiment(catg_path, stm_path)

        self.assertEqual(experiment.par_data, 'mock par data')
        mock_make_par.assert_called_with(experiment._catg_temporary_file_name, experiment._stm_temporary_file_name, experiment.parameters)

    def test_parameters_update(self):
        params = BaseExperiment.Parameters()
        params.update(kc=0.5, m=1.3)
        self.assertEqual(params.kc, 0.5)
        self.assertEqual(params.m, 1.3)
        self.assertEqual(params.il, 10.0)  # Default value
        self.assertEqual(params.cl, 5.0)   # Default value

if __name__ == '__main__':
    unittest.main()
