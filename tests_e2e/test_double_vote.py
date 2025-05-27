
def test_double_vote_not_allowed(client, unique_post_id, alice_token, bob_token):
    pid = unique_post_id
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {alice_token}"}, json={"body": "Post test"})

    # Commentatore terzo
    client.post("/register", json={"username": "cm1", "password": "p", "email": "cm1@example.com"})
    cm_token = client.post("/login", json={"username": "cm1", "password": "p"}).json()["token"]
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {cm_token}"}, json={"text": "Ciao"})

    # Bob vota una volta (valido)
    r = client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {bob_token}"}, json={"candidate": "cm1"})
    assert r.status_code == 200

    # Bob vota di nuovo → errore
    r = client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {bob_token}"}, json={"candidate": "cm1"})
    assert r.status_code == 400
