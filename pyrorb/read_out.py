

import pandas as pd

from pathlib import Path
import numpy as np


def find_median_one_ups(df_table):
    median_one_up = np.floor(df_table.shape[0]/2) + 1
    result_df = pd.DataFrame(columns=['pattern', 'peak'])
    print(median_one_up)

    for column in df_table:
        idx = df_table[column].rank(method='first') == median_one_up
        true_rows = df_table[column].index[idx]
        result_df.loc[column] = true_rows.values[0], df_table.loc[true_rows,
                                                                  column].values[0]
    return result_df


def extract_metadata_from_stm(file_path):
    p = Path(file_path)
    stm_file = p.parent / f'{p.stem}.stm'

    metadata = dict()
    with open(stm_file, 'r', encoding='iso-8859-1') as file:
        for line in file:
            if line.startswith('C'):
                if ':' in line:
                    k, v = [x.strip() for x in line.split(':', 1)]
                    k = k[1:].strip().replace('.', '')
                    metadata[k] = v

    return metadata


def read_sections(file_path):
    # Initialize variables to store sections
    sections = {'init': []}
    current_section = 'init'

    # Read the output file and parse sections
    with open(file_path, 'r', encoding='iso-8859-1') as file:

        current_section = 'init'
        for line in file:

            if line.startswith(' ******'):

                current_section = sections[current_section].pop()
                sections[current_section] = []

            else:
                sections[current_section].append(line)

    return sections


def read_hydrographs(sections):
    headers = None
    for line in sections[' Hydrograph summary\n']:
        if headers is None:
            if 'Inc    Time' in line:
                headers = line.split()
                df = pd.DataFrame(columns=headers[1:])
        else:
            this_line = line.replace('\n', '').split()
            df.loc[this_line[0]] = this_line[1:]

    return df.set_index('Time').astype(float)
