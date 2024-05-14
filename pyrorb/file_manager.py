import zipfile
import os
from glob import glob
from pathlib import Path


class FileManager:
    def __init__(self, save_path):
        self.save_path = save_path

    def create_parameters(self, files, k, m, il, cl):
        parameters = make_par_files(files, str(self.save_path), k=k, m=m, il=il, cl=cl)
        create_text_files(parameters)
        return parameters

    def create_zip(self, files, index):
        zip_filename = self.save_path / f'my_inputs_{index}.zip'
        create_zip(files, zip_filename)
        return zip_filename

    def cleanup_files(self, files):
        for file in files:
            print(file)
            os.remove(file)



def unzip_file(zip_file_path, extracted_directory):
    """
    Extract files from a ZIP archive to the specified directory.

    Args:
        zip_file_path (str): Path to the ZIP file.
        extracted_directory (str): Directory where files will be extracted.

    Returns:
        None
    """
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_directory)
    except Exception as e:
        print(f'Error extracting files: {str(e)}')

def create_zip(file_patterns, zip_filename):
    """
    Create a ZIP file containing files matching the specified patterns.

    Args:
        file_patterns (list): List of file patterns to include in the ZIP file.
        zip_filename (str): Name of the ZIP file to create.

    Returns:
        None
    """
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pattern in file_patterns:
            matching_files = glob(str(pattern))
            for file in matching_files:
                file_name = os.path.basename(file)
                zipf.write(file, file_name)

def create_text_files(strings_dict):
    """
    Create a zip file containing separate files for each string in the list.

    Args:
        strings (list): List of strings to be added as separate files in the zip file.
        zip_filename (str): Name of the zip file to create.

    Returns:
        None
    """
    for name, text in strings_dict.items():        
    
        # Create a temporary file and write the string content to it
        temp_file = name
        with open(temp_file, 'w') as file:
            file.write(text)

def make_par_files(file_list, output_dir, k=10, m=0.8, il=20, cl=2):
    files = [file for file_pattern in file_list for file in glob(str(file_pattern))]
    cfiles = [file for file in files if file.endswith('.catg')]
    sfiles = [file for file in files if file.endswith('.stm')]
    output_files = {}

    for cfile in cfiles:
        for sfile in sfiles:
            fn = Path(output_dir) / f'{Path(cfile).stem}_{Path(sfile).stem}.par'
            output_files[fn] = f"""# BEGIN
Cat file :{Path(cfile).stem}.catg
Stm file :{Path(sfile).stem}.stm
Lumped kc:T
Verbosity:3
Lossmodel:1
Num ISA  :1
ISA 1    :{k},{m}
Num burst:1
ISA 1    :{il},{cl}
# END"""

    return output_files
