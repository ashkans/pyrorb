import httpx
from pathlib import Path
from pyrorb import file_manager
import os
import uuid


class RorbClient:
    def __init__(self, save_path, url):
        self.save_path = save_path
        self.url = url

    def send_zip(self, filepath):
        client = httpx.Client(timeout=None)

        sd = Path(self.save_path)
        zip_path = sd/ f'results_{uuid.uuid4()}.zip'
        
        post_files = {
        "": open(filepath, "rb"),
        }
        headersList = {
        "Accept": "*/*",
        "User-Agent": "Thunder Client (https://www.thunderclient.com)" 
        }

        payload = ""

        data = client.post(self.url, files=post_files, headers=headersList)

        try:
            with open(zip_path, 'wb') as f:
                f.write(data.content)

            file_manager.unzip_file(zip_path, sd)
        finally:
            os.remove(zip_path)
