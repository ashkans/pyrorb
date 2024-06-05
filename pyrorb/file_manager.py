import os
import shutil
import tempfile
import zipfile
from glob import glob

from pyrorb.utils import make_par_files


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

def with_temp_dir(func, *args, **kwargs):
    """
    Creates a temporary directory, runs the given function with the directory path as an argument,
    and then deletes the directory after the function completes.

    :param func: A function that takes a single argument, the path to the temporary directory.

    ===

    # Example usage of the utility function
    def example_operations(temp_dir):
        temp_file_path = os.path.join(temp_dir, 'temp_file.txt')
        with open(temp_file_path, 'w') as temp_file:
            temp_file.write("This is some temporary data.")
        
        with open(temp_file_path, 'r') as temp_file:
            data = temp_file.read()
            print(f"Data read from temporary file: {data}")

    if __name__ == "__main__":
        with_temp_dir(example_operations)    
    """
    temp_dir = tempfile.mkdtemp()
    try:
        func(temp_dir, *args, **kwargs)

    finally:
        shutil.rmtree(temp_dir)
        