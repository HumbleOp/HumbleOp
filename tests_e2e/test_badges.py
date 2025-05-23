def test_insightful_badge(client, unique_post_id, alice_token):
    pid = unique_post_id
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {alice_token}"}, json={"body": "Post badge"})
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {alice_token}"}, json={"text": "Insightful comment"})

    for i in range(25):
        uname = f"u{i}"
        client.post("/register", json={"username": uname, "password": "p", "email": f"{uname}@example.com"})
        token = client.post("/login", json={"username": uname, "password": "p"}).json()["token"]
        client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"candidate": "alice"})

    client.post(f"/start_duel/{pid}", headers={"Authorization": f"Bearer {alice_token}"})

    r = client.get("/profile", headers={"Authorization": f"Bearer {alice_token}"})
    badges = r.json()["badges"]
    assert "Insightful" in badges


def test_serial_voter_badge(client, unique_post_id, alice_token):
    for i in range(10):
        pid = f"{unique_post_id}-v{i}"
        client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {alice_token}"}, json={"body": "P"})
        client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {alice_token}"}, json={"text": "C"})

        uname = f"target{i}"
        client.post("/register", json={"username": uname, "password": "x", "email": f"{uname}@example.com"})
        client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {alice_token}"}, json={"candidate": "alice"})

    r = client.get("/profile", headers={"Authorization": f"Bearer {alice_token}"})
    badges = r.json()["badges"]
    assert "Serial Voter" in badges


def test_consistent_debater_badge(client, alice_token):
    for i in range(10):
        pid = f"cd-{i}"
        client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {alice_token}"}, json={"body": "X"})
        client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {alice_token}"}, json={"text": "Y"})
        client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {alice_token}"}, json={"candidate": "alice"})
        client.post(f"/start_duel/{pid}", headers={"Authorization": f"Bearer {alice_token}"})

    r = client.get("/profile", headers={"Authorization": f"Bearer {alice_token}"})
    badges = r.json()["badges"]
    assert "Consistent Debater" in badges


def test_eloquent_speaker_badge(client, unique_post_id, alice_token):
    long_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 5

    for i in range(20):
        pid = f"elq-{unique_post_id}-{i}"
        client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {alice_token}"}, json={"body": "Z"})
        client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {alice_token}"}, json={"text": long_text})

    r = client.get("/profile", headers={"Authorization": f"Bearer {alice_token}"})
    badges = r.json()["badges"]
    assert "Eloquent Speaker" in badges
