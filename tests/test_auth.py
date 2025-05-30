def test_register_login_and_duplicate(client):
    # registra utente con email
    client.post("/register", json={"username": "alice", "password": "pwd", "email": "alice@example.com"})
    login_resp = client.post("/login", json={"username": "alice", "password": "pwd"})
    token1 = login_resp.get_json()["access_token"]

    # login
    rv = client.post("/login", json={"username": "alice", "password": "pwd"})
    assert rv.status_code == 200
    token2 = rv.get_json()["access_token"]
    assert token2 != token1  # token rigenerato

    # registrazione duplicata (username)
    rv = client.post("/register", json={"username": "alice", "password": "pwd", "email": "alice2@example.com"})
    assert rv.status_code == 409

    # registrazione duplicata (email)
    rv = client.post("/register", json={"username": "bob", "password": "pwd", "email": "alice@example.com"})
    assert rv.status_code == 409



def test_login_fail_wrong_password(client):
    client.post("/register", json={"username": "bob", "password": "pwd", "email": "bob@example.com"})
    rv = client.post("/login", json={"username": "bob", "password": "wrong"})
    assert rv.status_code == 401


def test_login_fail_nonexistent_user(client):
    rv = client.post("/login", json={"username": "ghost", "password": "x"})
    assert rv.status_code == 401


def test_register_missing_fields(client):
    # manca email
    rv = client.post("/register", json={"username": "x", "password": "p"})
    assert rv.status_code == 400

    # manca password
    rv = client.post("/register", json={"username": "x", "email": "x@example.com"})
    assert rv.status_code == 400

    # manca username
    rv = client.post("/register", json={"password": "p", "email": "x@example.com"})
    assert rv.status_code == 400

    # email non valida
    rv = client.post("/register", json={"username": "x", "password": "p", "email": "invalidemail"})
    assert rv.status_code == 400

def test_register_includes_email_flags(client, capsys):
    rv = client.post("/register", json={
        "username": "testmail",
        "password": "pw",
        "email": "test@example.com"
    })
    assert rv.status_code == 201

    # accedi al DB all'interno del contesto applicativo
    with client.application.app_context():
        from models import User
        user = User.query.filter_by(username="testmail").first()
        assert user is not None
        assert user.email == "test@example.com"
        assert user.email_verified is False
        assert user.reset_token is None

    # controlla che il verify link sia stampato
    captured = capsys.readouterr()
    assert "/verify/" in captured.out

