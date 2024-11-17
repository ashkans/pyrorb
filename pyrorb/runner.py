# imports
import os
from pathlib import Path
from typing import List, Callable

from dotenv import load_dotenv

from pyrorb.client import RorbClient
from pyrorb.config_manager import ConfigManager
from pyrorb.experiments.base_experiment import BaseExperiment
from pyrorb.file_manager import create_zip, with_temp_dir
from pyrorb.result import Result
from concurrent.futures import ThreadPoolExecutor
from functools import partial
#from tqdm import tqdm

load_dotenv()

class ExperimentRunner:
    '''
    Multiple experiments can be registered in this class.
    It should have the capability of batching the registered experiments and write their files (catg and stm) to a directory or zip file.
    Append a unique identifier to the .par name (before extension).
    Submit the job to the endpoint.
    Wait for the job to finish.
    Receive the resulting zip file, extract the files, read the resulting files, and produce a result object for each experiment. The result will have the identifier in its name.
    '''

    def __init__(self, experiments:List[BaseExperiment]=None, maximum_experiment_per_request:int=10):

        
        self.endpoint = os.getenv('PYRORB_ENDPOINT')
        self.experiments = []
        self.maximum_experiment_per_request = maximum_experiment_per_request

        self.rorb_client = RorbClient(self.endpoint, on_error='retry', max_retries=3)

        if experiments:
            for exp in experiments:
                self.register_experiment(exp)

    def register_experiment(self, experiment: BaseExperiment):
        self.experiments.append(experiment)
        

    def submit_batches_legecy(self, progress_callback: Callable[[int], None] = None):
        for i in range(0, len(self.experiments), self.maximum_experiment_per_request):

            batch = self.experiments[i:i+self.maximum_experiment_per_request]
            with_temp_dir(self._submit_batch, batch, batch_id=i, progress_callback=progress_callback)

    def submit_batches(self, progress_callback: Callable[[int], None] = None, show_progress_bar:bool=True):
        num_batches = (len(self.experiments) + self.maximum_experiment_per_request - 1) // self.maximum_experiment_per_request

        with ThreadPoolExecutor(200) as executor:
            futures = []
            # Submit all batches
            for i in range(0, len(self.experiments), self.maximum_experiment_per_request):
                batch = self.experiments[i:i+self.maximum_experiment_per_request]
                submit_func = partial(with_temp_dir, self._submit_batch, batch, batch_id=i, progress_callback=progress_callback)
                futures.append(executor.submit(submit_func))

            # Wait for all batches with progress bar
            try:
                import tqdm
            except ImportError:
                show_progress_bar = False

            if show_progress_bar:
                for future in tqdm.tqdm(futures, total=num_batches, desc="Processing batches", leave=False):
                    future.result()
            else:
                for future in futures:
                    future.result()

    
    @property
    def expeiment_map(self):
        return {exp.id: exp for exp in self.experiments}

    def _submit_batch(self, temp_dir, batch, batch_id='', progress_callback: Callable[[int], None] = None):
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

            if progress_callback:   
                progress_callback()
                
        



