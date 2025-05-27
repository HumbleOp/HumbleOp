
def test_flag_switches_winner_if_threshold_met(client, unique_post_id, alice_token):
    pid = unique_post_id
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {alice_token}"}, json={"body": "Flag this"})

    client.post("/register", json={"username": "cm", "password": "p", "email": "cm@example.com"})
    cm_token = client.post("/login", json={"username": "cm", "password": "p"}).json()["token"]
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {cm_token}"}, json={"text": "Commento"})

    # Altri commenti/voti/flag ecc. come prima
