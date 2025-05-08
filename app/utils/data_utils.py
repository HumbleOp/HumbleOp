import os
import json
from app.config.config import Config

def load_data(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_data(data, file_path):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)