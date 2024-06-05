
from jinja2 import Template

from pyrorb.utils import make_par

from pathlib import Path
import uuid

class BaseExperiment:
    '''
    This class is the base experiment of a rorb simulation.
    It serves only one single catg and only one storm file.
    It contains methods to amend the catg and stm.
    It maintains the point of truth in memory.
    It has methods to read and write catg and stm files.
    Running the experiment is handled by a runner class.
    '''

    class Parameters:
        def __init__(self, kc=0.4, m=1.2, il=10.0, cl=5.0):
            self.kc = kc
            self.m = m
            self.il = il
            self.cl = cl

        def update(self, kc=None, m=None, il=None, cl=None):
            if kc is not None:
                self.kc = kc
            if m is not None:
                self.m = m
            if il is not None:
                self.il = il
            if cl is not None:
                self.cl = cl

    def __init__(self, catg_file_path: str, stm_file_path: str, kc=0.4, m=1.2, il=10.0, cl=5.0, encoding='ISO-8859-1', id=None):
        self.catg_data = None
        self.stm_data = None
        self.parameters = self.Parameters(kc, m, il, cl)
        self.encoding = encoding
        self.catg_data = self._read_file(catg_file_path)
        self.stm_data = self._read_file(stm_file_path)

        if id is None:
            self.renew_id()
        else:
            self.id=id
        
    
    def renew_id(self):
        self.id=str(uuid.uuid4())[:8]

    @property
    def _catg_temporary_file_name(self):
        return f'catg{self.id}.catg'
        
    @property
    def _stm_temporary_file_name(self):
        return f'stm{self.id}.stm'

    @property
    def _par_temporary_file_name(self):
        return f'par{self.id}.par'


    def _read_file(self, file_path: str) -> str:
        with open(file_path, 'r', encoding=self.encoding) as file:
            return file.read()

    def _write_file(self, file_path: str, data: str):
        with open(file_path, 'w') as file:
            file.write(data)

    def write_par(self, path):
        self._write_file(Path(path)/self._par_temporary_file_name, self.par_data)

    def write_catg(self, path):
        self._write_file(Path(path)/self._catg_temporary_file_name, self.catg_data)

    def write_stm(self, path):
        self._write_file(Path(path)/self._stm_temporary_file_name, self.stm_data)

    def write_files(self, path):
        self.write_par(path)
        self.write_catg(path)
        self.write_stm(path)

    @property
    def par_data(self):
        return make_par(self._catg_temporary_file_name, self._stm_temporary_file_name, self.parameters)


    @property
    def stm_metadata(self):
    
        metadata = dict()
        for line in self.stm_data.split('\n'):
            if line.startswith('C'):
                if ':' in line:
                    k, v = [x.strip() for x in line.split(':', 1)]
                    k = k[1:].strip().replace('.', '')
                    metadata[k] = v

        return metadata
    
    @property
    def stm_duration(self):
        return self.stm_metadata['Storm duration']
    
    @property
    def stm_arin(self):
        return self.stm_metadata['Storm ARI (yr)']


if __name__ == "__main__":
    # sample use case:
    from pyrorb.config_manager import ConfigManager
    config = ConfigManager('./config.json')
    dataset_path = Path(config.get('sample_dataset'))
    catg_file_path = dataset_path / 'catg.catg'
    stm_file_path = dataset_path / 'stm.stm'
    exp = BaseExperiment(catg_file_path, stm_file_path, kc=0.4, m=1.2, il=10.0, cl=5.0)    
    print('='*64)
    print(exp.par_data)
    print('='*64)
    print(exp.catg_data)
    print('='*64)
    print(exp.stm_data)
    print('='*64)
    #exp.write_files(PATH_TO_SAVE)