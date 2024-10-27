from typing import Dict

def get_key(d, v):
    return list(d.keys())[list(d.values()).index(v)]


def get_median_peak(d: Dict[str, float], how='median'):
    '''
    This function finds the median peak and the key of the first value that is larger than the median peak. 
    Example:
    d = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    get_median_peak(d) returns ('c', 3)
    '''

    #x = res[0.4]['1 hour']
    l = len(d)
    median_idx = l//2
    if how == 'median':
        value = sorted(d.values())[median_idx]

    elif how == 'median_one_up':
        value = sorted(d.values())[median_idx+1]

    return get_key(d, value), value

def get_max_median_peak(d: Dict[str, Dict[str, float]]):
    '''
    This function finds the maximum median peak and the key of the first value that is larger than the median peak. 
    Example:
    d = {{'a': {'aa': 1, 'ab': 2, 'ac': 3, 'ad': 4}, 'b': {'ba': 2, 'bb': 3, 'bc': 4, 'bd': 5}}}
    get_max_median_peak(d) returns ('b', 'bc', 4)
    '''
    median_peaks = {sd: get_median_peak(peaks) for sd, peaks in d.items()}
    maxidx = max(median_peaks, key=lambda x: median_peaks[x][1])
    
    return maxidx, median_peaks[maxidx][0], median_peaks[maxidx][1]

def calculate_critical_storm_characteristics(experiments):
    # Initialize a dictionary to store experiment results
    experiment_results = {}

    # Process each experiment
    for exp in experiments:
        storm_duration = exp.stm_metadata['Storm duration']
        temporal_pattern = exp.stm_metadata['Temporal pattern']
        kc_value = exp.parameters.kc

        # Process each hydrograph in the experiment results
        for hydrograph_key in [key for key in exp.result.hydrographs.keys() if key != 'Time']:
            # Initialize nested dictionaries if they don't exist
            experiment_results.setdefault(hydrograph_key, {}).setdefault(kc_value, {}).setdefault(storm_duration, {})
            
            # Store the peak flow for this combination of parameters
            experiment_results[hydrograph_key][kc_value][storm_duration][temporal_pattern] = max(exp.result.hydrographs[hydrograph_key])

    # Initialize the output dictionary
    critical_storm_characteristics = {}

    # Analyze results for each hydrograph
    for hydrograph in experiment_results:
        critical_storm_characteristics[hydrograph] = {
            'peak': [],
            'critical_duration': [],
            'critical_pattern': [],
            'kc': []
        }
        
        # Find critical storm characteristics for each kc value
        for kc in experiment_results[hydrograph]:
            critical_duration, critical_pattern, peak_flow = get_max_median_peak(experiment_results[hydrograph][kc])
            
            critical_storm_characteristics[hydrograph]['peak'].append(peak_flow)
            critical_storm_characteristics[hydrograph]['critical_duration'].append(critical_duration)
            critical_storm_characteristics[hydrograph]['critical_pattern'].append(critical_pattern)
            critical_storm_characteristics[hydrograph]['kc'].append(float(kc))
    
    return critical_storm_characteristics

