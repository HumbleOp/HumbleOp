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


def award_badge(username, badge_name, users, save=True):
    """
    Award a badge to the user. If `save=False`, saving must be done manually.

    Args:
        username (str): The username of the user to award the badge to.
        badge_name (str): The name of the badge to award.
        users (dict): The dictionary of all users.
        save (bool): Whether to save the changes immediately. Defaults to True.
    """
    user = users.get(username)
    if not user:
        logging.warning(f"User '{username}' not found. Cannot award badge '{badge_name}'.")
        return

    # Ensure the user has a "badges" list and award the badge if not already present
    badges = user.setdefault("badges", [])
    if badge_name not in badges:
        badges.append(badge_name)
        logging.info(f"Awarded badge '{badge_name}' to user '{username}'.")

        if save:
            save_users(users)
            logging.info(f"Changes saved after awarding badge '{badge_name}' to user '{username}'.")
