import uuid
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from .client import RorbClient
from .file_manager import FileManager

class RorbProcessor:
    def __init__(self, catg_files, storm_files, endpoint, save_path='temp', folder_name=None):

        self.folder_name=folder_name or str(uuid.uuid4())
        self.save_path = Path(save_path) / self.folder_name
        self.save_path.mkdir(parents=True, exist_ok=True)

        self.endpoint=endpoint
        self.catg_files = catg_files
        self.storm_files=storm_files
        
        self.kc=1.5
        self.m=0.8
        self.il=20
        self.cl=2

        self.fm = FileManager(self.save_path)
        self.rorb_client = RorbClient(self.save_path, self.endpoint)

        self.chunk_size=20

        self.to_be_cleared=[]
    
    def amend_catg(self, find_text, replace_with, suffix=None):
        # TODO: make sure only and only one occurance of the find_txt is there.
        
        self.original_catg_files = self.catg_files
        new_catg_files = []
        suffix = suffix or str(uuid.uuid4())[:4]
        for file in self.catg_files:
            save_to = self.save_path/(Path(file).stem+suffix+Path(file).suffix)
            with open(file, 'r') as f:
                txt = f.read()
            txt=txt.replace(find_text, replace_with)

            with open(save_to, 'w') as f:
                f.write(txt)

            new_catg_files.append(save_to)
        self.catg_files= new_catg_files
        self.to_be_cleared += new_catg_files

    @property
    def file_list(self):
        return self.catg_files+self.storm_files
    
    @property
    def parameters(self):
        
        return self.fm.create_parameters(self.file_list, self.kc, self.m,self.il, self.cl)      

    @property
    def parameter_keys(self):
        return list(self.parameters.keys())

    def process_chunk(self, chunk_index):
        i = chunk_index * self.chunk_size
        zip_filename = self.fm.create_zip(self.file_list + self.parameter_keys[i:i+self.chunk_size], i)
        self.rorb_client.send_zip(zip_filename)
        self.to_be_cleared += list(self.parameters.keys()) + [zip_filename]

    def cleanup(self):
        self.fm.cleanup_files(self.to_be_cleared)
        self.to_be_cleared=[]
        self.catg_files=self.original_catg_files
        

    def run_parallel(self):
        # This is only works for complete chunks, should be fixed.
        num_chunks = len(self.parameters) // self.chunk_size
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(self.process_chunk, range(num_chunks))