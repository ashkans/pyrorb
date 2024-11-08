import httpx
from pathlib import Path
from pyrorb import file_manager
import os
import uuid
import warnings

class RorbClient:
    def __init__(self, url, on_error='raise', max_retries=3):
        self.url = url
        self.on_error = on_error
        self.max_retries = max_retries

    def send_zip(self, save_dir, post_file_path, retry_count=0):
        client = httpx.Client(timeout=None)
        save_dir = Path(save_dir)
        zip_path = save_dir / f'results_{uuid.uuid4()}.zip'

        post_files = {
            "": open(post_file_path, "rb"),
        }
        headersList = {
            "Accept": "*/*",
            "User-Agent": "Thunder Client (https://www.thunderclient.com)"
        }

        payload = ""
        
        data = client.post(self.url, files=post_files, headers=headersList)

        # Handle data.status_code
        if data.status_code == 200:
            try:
                with open(zip_path, 'wb') as f:
                    f.write(data.content)
                file_manager.unzip_file(zip_path, save_dir)
            finally:
                os.remove(zip_path)
        else:
            if self.on_error == 'raise':
                raise httpx.HTTPStatusError(f"Request failed with status code {data.status_code}", request=data.request, response=data)
            elif self.on_error == 'warn':
                warnings.warn(f"Request failed with status code {data.status_code}")
            elif self.on_error == 'retry':
                if retry_count < self.max_retries:
                    return self.send_zip(save_dir, post_file_path, retry_count + 1)
                else:
                    raise httpx.HTTPStatusError(f"Request failed with status code {data.status_code}", request=data.request, response=data)
                
            else:
                raise ValueError(f"Invalid value for on_error: {self.on_error}")

# Example usage
# client = RorbClient('http://example.com/upload', raise_on_error=True)
# client.send_zip('/path/to/save_dir', '/path/to/post_file.zip')
