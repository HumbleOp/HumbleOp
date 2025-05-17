# tests/test_auth.py

def test_register_login_and_duplicate(client):
    # registra utente
    rv = client.post("/register", json={"username": "alice", "password": "pwd"})
    assert rv.status_code == 201
    token1 = rv.get_json()["token"]

    # login
    rv = client.post("/login", json={"username": "alice", "password": "pwd"})
    assert rv.status_code == 200
    token2 = rv.get_json()["token"]
    assert token2 != token1  # token rigenerato

    # registrazione duplicata
    rv = client.post("/register", json={"username": "alice", "password": "pwd"})
    assert rv.status_code == 409

def test_login_fail_wrong_password(client):
    client.post("/register", json={"username": "bob", "password": "pwd"})
    rv = client.post("/login", json={"username": "bob", "password": "wrong"})
    assert rv.status_code == 401

def test_login_fail_nonexistent_user(client):
    rv = client.post("/login", json={"username": "ghost", "password": "x"})
    assert rv.status_code == 401
