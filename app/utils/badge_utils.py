import json
from app.config.config import Config

def load_users():
    try:
        with open(Config.USERS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users(users):
    with open(Config.USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def award_badge(username, badge_name, users, save=True):
    """
    Award a badge to the user. If `save=False`, saving must be done manually.
    """
    user = users.get(username)
    if not user:
        return

    if badge_name not in user.get("badges", []):
        user.setdefault("badges", []).append(badge_name)
        if save:
            save_users(users)
