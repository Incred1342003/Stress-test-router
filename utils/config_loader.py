import yaml
import os

def load_config():
    # Get absolute path to config.yaml relative to this file
    base_dir = os.path.dirname(os.path.dirname(__file__))  # goes from utils → project root
    config_path = os.path.join(base_dir, "config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
