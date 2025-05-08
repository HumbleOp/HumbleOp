import os
import logging

# Set up logging for debugging
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO").upper())

# Define the base directory of the current file
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, '../../humbleop.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File paths with fallback to environment variables
    USERS_FILE = os.environ.get("USERS_FILE", os.path.abspath(os.path.join(BASE_DIR, '../../users.json')))
    DATA_FILE = os.environ.get("DATA_FILE", os.path.abspath(os.path.join(BASE_DIR, '../../data.json')))

    @staticmethod
    def ensure_files_exist():
        """
        Ensures that USERS_FILE and DATA_FILE exist. Creates them if missing.
        """
        for file_path in [Config.USERS_FILE, Config.DATA_FILE]:
            if not os.path.exists(file_path):
                logging.warning(f"{file_path} not found. Creating an empty JSON file.")
                try:
                    with open(file_path, 'w') as f:
                        f.write('{}')  # or default JSON data
                    os.chmod(file_path, 0o600)  # Optional: Restrict file permissions
                except IOError as e:
                    logging.error(f"Failed to create {file_path}: {e}")
                    raise

# Log the paths for debugging
logging.info(f"USERS_FILE path: {Config.USERS_FILE}")
logging.info(f"DATA_FILE path: {Config.DATA_FILE}")

# Ensure critical files exist
Config.ensure_files_exist()