import pandas as pd

from pathlib import Path
import numpy as np


class Result():
    def __init__(self, resutl_file):
        self.result_tile = resutl_file
        self.sections=self.read_sections(resutl_file)
        self.hydrographs = self.read_hydrographs(self.sections)
        

    @staticmethod     
    def read_sections(file_path):
        # Initialize variables to store sections
        sections = {'init': []}
        current_section = 'init'

        # Read the output file and parse sections
        with open(file_path, 'r', encoding='iso-8859-1') as file:

            current_section = 'init'
            for line in file:

                if line.startswith(' ******'):

                    current_section = sections[current_section].pop().strip().replace('\n', '').replace(':', '')
                    sections[current_section] = []

                else:
                    sections[current_section].append(line)

        return sections

    @staticmethod
    def read_hydrographs(sections):
        headers = None
        for line in sections['Hydrograph summary']:
            if headers is None:
                if 'Inc    Time' in line:
                    headers = line.split()
                    df = pd.DataFrame(columns=headers[1:])
            else:
                this_line = line.replace('\n', '').split()
                df.loc[this_line[0]] = this_line[1:]

        return df.set_index('Time').astype(float)
    
    
    




   




    
