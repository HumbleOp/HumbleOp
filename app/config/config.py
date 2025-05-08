import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, '../../humbleop.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    USERS_FILE = "users.json"
    DATA_FILE = "data.json"