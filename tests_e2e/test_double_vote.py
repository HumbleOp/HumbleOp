def test_double_vote_not_allowed(client, unique_post_id, alice_token, bob_token):
    pid = unique_post_id

    # Alice crea e commenta
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {alice_token}"}, json={"body": "Post test"})
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {alice_token}"}, json={"text": "Ciao"})

    # Bob vota per Alice (1° voto, valido)
    r = client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {bob_token}"}, json={"candidate": "alice"})
    assert r.status_code == 200

    # Bob prova a votare di nuovo (deve fallire)
    r = client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {bob_token}"}, json={"candidate": "alice"})
    assert r.status_code == 403
    assert "already voted" in r.text
