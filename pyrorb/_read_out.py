
from pathlib import Path
import numpy as np


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
    hydrographs = {}
    for line in sections[' Hydrograph summary\n']:
        if headers is None:
            if 'Inc    Time' in line:
                headers = line.split()
                for header in headers[1:]:
                    hydrographs[header] = []
        else:
            this_line = line.replace('\n', '').split()
            time = this_line[0]
            for i, header in enumerate(headers[1:], 1):
                hydrographs[header].append((time, float(this_line[i])))

    return hydrographs
