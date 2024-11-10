import json
import os

def load_config():
    # Use absolute path to the 'Bot.setup.json' file from the root directory
    config_file_path = os.path.join(os.path.dirname(__file__), '..', 'Bot\\setup.json')
    config_file_path = os.path.abspath(config_file_path)  # Get the absolute path to the file
    
    with open(config_file_path, 'r') as file:
        config = json.load(file)
    return config