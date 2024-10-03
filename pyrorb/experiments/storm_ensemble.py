from typing import List

from pyrorb.experiments.base_experiment import BaseExperiment


class StormEnsembleExperiment:
    def __init__(self, catg_file_path: str, stm_file_paths: List[str], kc=0.4, m=1.2, il=10.0, cl=5.0, encoding='ISO-8859-1'):
        self.catg_file_path = catg_file_path
        self.stm_file_paths = stm_file_paths
        self.parameters = BaseExperiment.Parameters(kc, m, il, cl)
        self.encoding = encoding
        self.experiments = self._create_experiments()

    def _create_experiments(self):
        experiments = []
        for stm_file_path in self.stm_file_paths:
            exp = BaseExperiment(self.catg_file_path, stm_file_path, self.parameters.kc, self.parameters.m, self.parameters.il, self.parameters.cl, self.encoding)
            experiments.append(exp)
        return experiments

    def write_files(self, path):
        for exp in self.experiments:
            exp.write_files(path)

    def run_experiments(self, runner):
        for exp in self.experiments:
            runner.register_experiment(exp)
        runner.submit_batches()