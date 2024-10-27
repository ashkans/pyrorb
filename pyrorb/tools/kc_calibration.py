from pyrorb.runner import ExperimentRunner
from pyrorb.experiments.base_experiment import BaseExperiment
from typing import Callable

from .kc_calibration_utils import calculate_critical_storm_characteristics


def kc_calibration(catg_data: str, stm_data_list: list[str], kc_range: list[float], m: float, il: float, cl: float, progress_callback: Callable[[int], None] = None):

    Experiments = []

    print('Creating experiments...')

    for stm_data in stm_data_list:
        for kc in kc_range:  
            Experiments.append(BaseExperiment(catg_data, stm_data, kc=kc, m=m, il=il, cl=cl))

    runner = ExperimentRunner(experiments=Experiments)

    
    runner.submit_batches()
    return calculate_critical_storm_characteristics(runner.experiments)
    
