
def test_full_duel_flow(client, unique_post_id, alice_token, bob_token):
    post_id = unique_post_id
    client.post(f"/create_post/{post_id}", headers={"Authorization": f"Bearer {alice_token}"}, json={"body": "Questo è un post di Alice"})

    # Bob commenta invece di Alice
    client.post(f"/comment/{post_id}", headers={"Authorization": f"Bearer {bob_token}"}, json={"text": "Commento iniziale"})

    # Voti e duel partono normalmente
    client.post(f"/vote/{post_id}", headers={"Authorization": f"Bearer {alice_token}"}, json={"candidate": "bob"})
    client.post(f"/start_duel/{post_id}", headers={"Authorization": f"Bearer {alice_token}"})
    res = client.get(f"/results/{post_id}", headers={"Authorization": f"Bearer {alice_token}"}).json()
    assert "winner" in res
