import json

class ConfigManager:
    def __init__(self, filename):
        self.filename = filename
        self.config = self.load_config()

    def load_config(self):
        """Load the configuration file."""
        try:
            with open(self.filename, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            raise Exception(f"Configuration file {self.filename} not found.")
        except json.JSONDecodeError:
            raise Exception(f"Error decoding the JSON from the file {self.filename}.")

    def get(self, key, default=None):
        """Retrieve a value from the configuration with a default if the key does not exist."""
        return self.config.get(key, default)
