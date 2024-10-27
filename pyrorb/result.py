class Result():
    def __init__(self, result_file):
        self.result_file = result_file
        self.sections = self.read_sections(result_file)
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
        hydrographs = {}
        for line in sections['Hydrograph summary']:
            if headers is None:
                if 'Inc    Time' in line:
                    headers = line.split()[1:]
                    for header in headers:
                        hydrographs[header] = []
            else:
                this_line = line.replace('\n', '').split()
                time = this_line[0]
                for i, header in enumerate(headers):
                    hydrographs[header].append(float(this_line[i+1]))

        return hydrographs
