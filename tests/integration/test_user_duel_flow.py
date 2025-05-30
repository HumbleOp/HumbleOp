import uuid

import uuid

def test_full_user_duel_flow(client, auth_token):
    # Genera nomi univoci
    alice_name = f"alice_{uuid.uuid4().hex[:8]}"
    bob_name = f"bob_{uuid.uuid4().hex[:8]}"
    charlie_name = f"charlie_{uuid.uuid4().hex[:8]}"

    # Registrazioni
    client.post("/register", json={
        "username": bob_name,
        "password": "hunter2",
        "email": f"{bob_name}@example.com"
    })
    bob_token = client.post("/login", json={
        "username": bob_name,
        "password": "hunter2"
    }).get_json()["access_token"]

    client.post("/register", json={
        "username": alice_name,
        "password": "hunter2",
        "email": f"{alice_name}@example.com"
    })
    alice_token = client.post("/login", json={
        "username": alice_name,
        "password": "hunter2"
    }).get_json()["access_token"]

    client.post("/register", json={
        "username": charlie_name,
        "password": "hunter2",
        "email": f"{charlie_name}@example.com"
    })
    charlie_token = client.post("/login", json={
        "username": charlie_name,
        "password": "hunter2"
    }).get_json()["access_token"]

    for _ in range(10):
        post_id = uuid.uuid4().hex

        # Bob crea il post
        resp = client.post(
            f"/create_post/{post_id}",
            headers={"Authorization": f"Bearer {bob_token}"},
            json={"body": "Post by Bob"}
        )
        assert resp.status_code == 200

        # Alice commenta
        resp = client.post(
            f"/comment/{post_id}",
            headers={"Authorization": f"Bearer {alice_token}"},
            json={"text": "Commento da Alice"}
        )
        assert resp.status_code == 200

        # Charlie commenta
        resp = client.post(
            f"/comment/{post_id}",
            headers={"Authorization": f"Bearer {charlie_token}"},
            json={"text": "Commento da Charlie"}
        )
        assert resp.status_code == 200

        # Charlie vota per Alice
        resp = client.post(
            f"/vote/{post_id}",
            headers={"Authorization": f"Bearer {charlie_token}"},
            json={"candidate": alice_name}
        )
        assert resp.status_code == 200

        # Charlie avvia il duello
        resp = client.post(
            f"/start_duel/{post_id}",
            headers={"Authorization": f"Bearer {charlie_token}"}
        )
        assert resp.status_code == 200

    # Verifica badge di Alice
    rv = client.get("/profile", headers={"Authorization": f"Bearer {alice_token}"})
    assert "Consistent Debater" in rv.get_json()["badges"]
