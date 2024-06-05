import unittest
from unittest.mock import patch, mock_open
import httpx
from pathlib import Path
from pyrorb import file_manager
import os
import uuid
import warnings
from pyrorb.client import RorbClient

# Mocking necessary parts
def mock_unzip_file(zip_path, save_dir):
    pass

class TestRorbClient(unittest.TestCase):
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('httpx.Client.post')
    @patch('os.remove')
    @patch('pyrorb.file_manager.unzip_file', side_effect=mock_unzip_file)
    def test_send_zip_success(self, mock_unzip, mock_remove, mock_post, mock_file):
        # Setup
        mock_post.return_value.status_code = 200
        mock_post.return_value.content = b'fake content'
        
        client = RorbClient('http://example.com/upload')
        save_dir = '/path/to/save_dir'
        post_file_path = '/path/to/post_file.zip'
        
        # Execute
        client.send_zip(save_dir, post_file_path)
        
        # Verify
        mock_post.assert_called_once()
        #mock_file.assert_called_once_with(post_file_path, 'rb') should called twice
        mock_unzip.assert_called_once()
        mock_remove.assert_called_once()

    @patch('builtins.open', new_callable=mock_open)
    @patch('httpx.Client.post')
    def test_send_zip_failure_with_exception(self, mock_post, mock_file):
        # Setup
        mock_post.return_value.status_code = 500
        
        client = RorbClient('http://example.com/upload', raise_on_error=True)
        save_dir = '/path/to/save_dir'
        post_file_path = '/path/to/post_file.zip'
        
        # Execute and Verify
        with self.assertRaises(httpx.HTTPStatusError):
            client.send_zip(save_dir, post_file_path)
        
        mock_post.assert_called_once()
        mock_file.assert_called_once_with(post_file_path, 'rb')

    @patch('builtins.open', new_callable=mock_open)
    @patch('httpx.Client.post')
    @patch('warnings.warn')
    def test_send_zip_failure_with_warning(self, mock_warn, mock_post, mock_file):
        # Setup
        mock_post.return_value.status_code = 500
        
        client = RorbClient('http://example.com/upload', raise_on_error=False)
        save_dir = '/path/to/save_dir'
        post_file_path = '/path/to/post_file.zip'
        
        # Execute
        client.send_zip(save_dir, post_file_path)
        
        # Verify
        mock_post.assert_called_once()
        mock_file.assert_called_once_with(post_file_path, 'rb')
        mock_warn.assert_called_once_with(f"Request failed with status code 500")

if __name__ == '__main__':
    unittest.main()
