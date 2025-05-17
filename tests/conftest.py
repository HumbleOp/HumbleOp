import os
import tempfile
import pytest
from app import create_app
from core.extensions import db, scheduler

@pytest.fixture
def client():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        db_path = tf.name

    config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    }

    app = create_app(config)

    with app.app_context():
        db.create_all()

    yield app.test_client()

    try:
        os.remove(db_path)
    except PermissionError:
        pass
