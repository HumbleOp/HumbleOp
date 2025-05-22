import os
import tempfile
import pytest
from app import create_app
from core.extensions import db, scheduler


@pytest.fixture
def client():
    # crea un database SQLite temporaneo
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


@pytest.fixture
def auth_token(client):
    """
    Registra e logga automaticamente un utente 'alice', restituisce il suo token.
    Utile per i test di integrazione che usano la fixture auth_token.
    """
    # 1) Register obbligatorio con email
    resp = client.post("/register", json={
        "username": "alice",
        "password": "secret",
        "email": "alice@example.com"
    })
    assert resp.status_code == 201, f"Register failed: {resp.data}"
    data = resp.get_json()
    token = data.get("token")
    assert token, "Response JSON must include 'token'"

    # 2) Login per rigenerare il token (alcuni test lo fanno)
    resp = client.post("/login", json={
        "username": "alice",
        "password": "secret"
    })
    assert resp.status_code == 200, f"Login failed: {resp.data}"
    token = resp.get_json().get("token")
    assert token, "Login response JSON must include 'token'"

    return token
