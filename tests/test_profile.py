import io
from models import User

def test_get_update_profile(client):
    rv = client.post("/register", json={ "username": "a", "password": "p", "email": "a@example.com" })
    token = rv.get_json()["token"]

    rv = client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    data = rv.get_json()
    assert data["username"] == "a"

    rv = client.put("/profile", headers={"Authorization": f"Bearer {token}"}, json={"bio": "ciao", "avatar_url": "x.png"})
    assert rv.status_code == 200
    assert rv.get_json()["profile"]["bio"] == "ciao"


def test_follow_unfollow_flow(client):
    # registra due utenti
    ta = client.post("/register", json={ "username": "a", "password": "p", "email": "a@example.com" }).get_json()["token"]
    tb = client.post("/register", json={ "username": "b", "password": "p", "email": "b@example.com" }).get_json()["token"]

    # a segue b
    rv = client.post("/follow/b", headers={"Authorization": f"Bearer {ta}"})
    assert rv.status_code == 200

    # a è nei following
    rv = client.get("/following", headers={"Authorization": f"Bearer {ta}"})
    assert "b" in rv.get_json()["following"]

    # b vede a nei followers
    rv = client.get("/followers", headers={"Authorization": f"Bearer {tb}"})
    assert "a" in rv.get_json()["followers"]

    # a unfollow b
    rv = client.post("/unfollow/b", headers={"Authorization": f"Bearer {ta}"})
    assert rv.status_code == 200

    # follow tolto
    rv = client.get("/following", headers={"Authorization": f"Bearer {ta}"})
    assert rv.get_json()["following"] == []

def test_upload_avatar_success(client):
    # registra utente e ottieni token
    rv = client.post("/register", json={ "username": "ava", "password": "test", "email": "ava@example.com" })
    token = rv.get_json()["token"]

    # immagine fake in memoria
    img = (io.BytesIO(b"fake image content"), "avatar.png")

    rv = client.post(
        "/upload_avatar",
        headers={"Authorization": f"Bearer {token}"},
        data={"avatar": img},
        content_type="multipart/form-data"
    )

    assert rv.status_code == 200
    assert "avatar_url" in rv.get_json()

def test_upload_avatar_missing_file(client):
    rv = client.post("/register", json={ "username": "noimg", "password": "p", "email": "noimg@example.com" }).get_json()
    token = rv["token"]

    rv = client.post(
        "/upload_avatar",
        headers={"Authorization": f"Bearer {token}"},
        data={},  # niente file
        content_type="multipart/form-data"
    )

    assert rv.status_code == 400
    assert "error" in rv.get_json()

def test_upload_avatar_invalid_extension(client):
    rv = client.post("/register", json={ "username": "badext", "password": "p", "email": "badext@example.com" }).get_json()
    token = rv["token"]

    # file con estensione non valida
    txt = (io.BytesIO(b"not an image"), "avatar.exe")

    rv = client.post(
        "/upload_avatar",
        headers={"Authorization": f"Bearer {token}"},
        data={"avatar": txt},
        content_type="multipart/form-data"
    )

    assert rv.status_code == 400
    assert "Invalid file type" in rv.get_json()["error"]

def test_upload_avatar_empty_filename(client):
    rv = client.post("/register", json={ "username": "nofile", "password": "p", "email": "nofile@example.com" }).get_json()
    token = rv["token"]

    # filename vuoto
    fake = (io.BytesIO(b""), "")

    rv = client.post(
        "/upload_avatar",
        headers={"Authorization": f"Bearer {token}"},
        data={"avatar": fake},
        content_type="multipart/form-data"
    )

    assert rv.status_code == 400
    assert "No selected file" in rv.get_json()["error"]