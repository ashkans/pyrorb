# imports
from pyrorb.experiments.base_experiment import BaseExperiment
from pyrorb.file_manager import create_zip, with_temp_dir
from pathlib import Path
from pyrorb.client import RorbClient
from pyrorb.result import Result
from pyrorb.config_manager import ConfigManager
from typing import List

class ExperimentRunner:
    '''
    Multiple experiments can be registered in this class.
    It should have the capability of batching the registered experiments and write their files (catg and stm) to a directory or zip file.
    Append a unique identifier to the .par name (before extension).
    Submit the job to the endpoint.
    Wait for the job to finish.
    Receive the resulting zip file, extract the files, read the resulting files, and produce a result object for each experiment. The result will have the identifier in its name.
    '''

    def __init__(self, config:ConfigManager, experiments:List[BaseExperiment]=None):

        
        self.endpoint = config.get('endpoint')
        self.experiments = []
        self.maximum_experiment_per_request = 20

        self.rorb_client = RorbClient(self.endpoint)

        if experiments:
            for exp in experiments:
                self.register_experiment(exp)

    def register_experiment(self, experiment: BaseExperiment):
        self.experiments.append(experiment)
        

    def submit_batches(self):
        for i in range(0, len(self.experiments), self.maximum_experiment_per_request):
            batch = self.experiments[i:i+self.maximum_experiment_per_request]
            with_temp_dir(self._submit_batch, batch, batch_id=i)

    
    @property
    def expeiment_map(self):
        return {exp.id: exp for exp in self.experiments}

    def _submit_batch(self, temp_dir, batch, batch_id=''):
        '''submit the batch to the endpoint.'''
        for exp in batch:
            exp.write_files(temp_dir)

        file_patterns = [str(Path(temp_dir) / f'*.{x}') for x in ['stm', 'par', 'catg']]
        zip_filename = str(Path(temp_dir) / f'batch_{batch_id}.zip' ) 
        create_zip(file_patterns, zip_filename)

        # submit the batch to the endpoint.
        self.rorb_client.send_zip(temp_dir, zip_filename)

        # read the results
        for exp in batch:
            outputs = list(Path(temp_dir).glob(f'*{exp.id}.out'))
            if len(outputs) > 1:
                pass
                # handel more than one file is found the first one is being used
            elif len(outputs) < 1:
                # handel no output is found
                pass
            
            else:
                output = outputs[0]



            exp.result = Result(output)
                
        



