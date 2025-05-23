def test_full_duel_flow(client, unique_post_id, alice_token, bob_token):
    post_id = unique_post_id

    # 1. Alice crea un post
    r = client.post(
        f"/create_post/{post_id}",
        headers={"Authorization": f"Bearer {alice_token}"},
        json={"body": "Questo è un post di Alice"}
    )
    assert r.status_code == 200

    # 2. Alice commenta il post
    r = client.post(
        f"/comment/{post_id}",
        headers={"Authorization": f"Bearer {alice_token}"},
        json={"text": "Commento iniziale"}
    )
    assert r.status_code == 200

    # 3. Bob vota per Alice
    r = client.post(
        f"/vote/{post_id}",
        headers={"Authorization": f"Bearer {bob_token}"},
        json={"candidate": "alice"}
    )
    assert r.status_code == 200

    # 4. Bob avvia il duello
    r = client.post(
        f"/start_duel/{post_id}",
        headers={"Authorization": f"Bearer {bob_token}"}
    )
    assert r.status_code == 200
    assert r.json()["winner"] == "alice"

    # 5. Alice vota per sé stessa
    r = client.post(
        f"/vote/{post_id}",
        headers={"Authorization": f"Bearer {alice_token}"},
        json={"candidate": "alice"}
    )
    assert r.status_code == 200

    # 6. Verifica badge su profilo
    r = client.get(
        "/profile",
        headers={"Authorization": f"Bearer {alice_token}"}
    )
    assert r.status_code == 200
    badges = r.json()["badges"]
    assert "First blood" in badges

def test_create_post_and_duel(client, unique_post_id, alice_token, bob_token):
    pid = unique_post_id

    r = client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {alice_token}"}, json={"body": "E2E Post"})
    assert r.status_code == 200

    r = client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {alice_token}"}, json={"text": "Commento"})
    assert r.status_code == 200

    r = client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {bob_token}"}, json={"candidate": "alice"})
    assert r.status_code == 200

    r = client.post(f"/start_duel/{pid}", headers={"Authorization": f"Bearer {bob_token}"})
    assert r.status_code == 200
