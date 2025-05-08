import json
from app.config.config import Config

def award_badge(username, badge_name, users):
    user = users.get(username)
    if not user:
        return
    if badge_name not in user["badges"]:
        user["badges"].append(badge_name)
        save_users(users)

def save_users(users):
    with open(Config.USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)