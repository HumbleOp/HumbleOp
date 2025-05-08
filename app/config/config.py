import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, '../../humbleop.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Absolute paths for USERS_FILE and DATA_FILE
    USERS_FILE = os.path.abspath(os.path.join(BASE_DIR, '../../users.json'))
    DATA_FILE = os.path.abspath(os.path.join(BASE_DIR, '../../data.json'))