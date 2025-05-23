import pytest
import httpx

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="session")
def client():
    return httpx.Client(base_url=BASE_URL)

@pytest.fixture
def unique_post_id():
    import uuid
    return uuid.uuid4().hex

@pytest.fixture
def alice_token(client):
    client.post("/register", json={"username": "alice", "password": "p", "email": "alice@example.com"})
    r = client.post("/login", json={"username": "alice", "password": "p"})
    return r.json()["token"]

@pytest.fixture
def bob_token(client):
    client.post("/register", json={"username": "bob", "password": "p", "email": "bob@example.com"})
    r = client.post("/login", json={"username": "bob", "password": "p"})
    return r.json()["token"]
