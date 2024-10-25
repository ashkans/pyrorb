import pandas as pd
from pyrorb.runner import ExperimentRunner
from pyrorb.experiments.base_experiment import BaseExperiment
from typing import Callable
def get_hydrograph_keys(experiments):
    return experiments[0].result.hydrographs.columns.to_list()

def get_peaks(experiments):
    df_list = []
    for exp in experiments:
        df_list.append(pd.DataFrame({
            'temporal_pattern': exp.stm_metadata['Temporal pattern'],
            'storm_duration': exp.stm_metadata['Storm duration'],
            'peak': exp.result.hydrographs.max(),
            'kc': exp.parameters.kc
        }))
    
    return pd.concat(df_list).reset_index()

def get_median_one_up(series):
    median = series.median()
    larger_than_median = series[series > median]
    return larger_than_median.idxmin(), larger_than_median.min()

def get_critical_storm(df_pivoted):
    max_value = float('-inf')
    max_duration = None
    max_pattern = None
    
    for duration, row in df_pivoted.iterrows():
        median_pattern, median_value = get_median_one_up(row)
        if median_value > max_value:
            max_value = median_value
            max_duration = duration
            max_pattern = median_pattern
    
    return float(max_value), max_duration, max_pattern

def get_median_one_up_for_all_hydrographs(experiments): 
    df = get_peaks(experiments)
    hydrograph_keys = get_hydrograph_keys(experiments)
    kc_values = df['kc'].unique()
    
    results = {key: {'peak': [], 'critical_duration': [], 'critical_pattern': [], 'kc': []} for key in hydrograph_keys}
    
    for key in hydrograph_keys:
        for kc in kc_values:
            df_pivoted = df[(df['index'] == key) & (df['kc'] == kc)].pivot_table(
                index='storm_duration', columns='temporal_pattern', values='peak'
            )
            
            peak, duration, pattern = get_critical_storm(df_pivoted)
            
            results[key]['peak'].append(peak)
            results[key]['critical_duration'].append(duration)
            results[key]['critical_pattern'].append(pattern)
            results[key]['kc'].append(float(kc))

    return results



def kc_calibration(catg_data: str, stm_data_list: list[str], kc_range: list[float], m: float, il: float, cl: float, progress_callback: Callable[[int], None] = None):

    Experiments = []

    print('Creating experiments...')

    for stm_data in stm_data_list:
        for kc in kc_range:  
            Experiments.append(BaseExperiment(catg_data, stm_data, kc=kc, m=m, il=il, cl=cl))

    runner = ExperimentRunner(experiments=Experiments)

    print(runner.endpoint)
    runner.submit_batches()
    return get_median_one_up_for_all_hydrographs(runner.experiments)
    
