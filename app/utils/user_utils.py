import json
import logging
from app.config.config import Config

def load_users():
    """
    Load user data from the configured USERS_FILE.
    Returns an empty dictionary if the file doesn't exist or contains invalid JSON.
    """
    try:
        with open(Config.USERS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"User file '{Config.USERS_FILE}' not found. Returning an empty dictionary.")
        return {}
    except json.JSONDecodeError:
        logging.error(f"User file '{Config.USERS_FILE}' contains invalid JSON. Returning an empty dictionary.")
        return {}

def save_users(users):
    """
    Save user data to the configured USERS_FILE.
    Logs an error if saving fails.
    """
    try:
        with open(Config.USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        logging.error(f"Failed to save user data to '{Config.USERS_FILE}': {e}")