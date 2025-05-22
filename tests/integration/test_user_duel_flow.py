import uuid

def test_full_user_duel_flow(client, auth_token):
    # Register Bob once
    resp = client.post('/register', json={
        'username': 'bob',
        'password': 'hunter2',
        'email': 'bob@example.com'
    })
    assert resp.status_code == 201
    resp = client.post('/login', json={
        'username': 'bob',
        'password': 'hunter2'
    })
    assert resp.status_code == 200
    bob_token = resp.get_json()['token']

    # Perform 10 full duel flows to trigger "Consistent Debater" badge
    for _ in range(10):
        # 1) Alice crea un post
        post_id = uuid.uuid4().hex
        resp = client.post(
            f'/create_post/{post_id}',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'body': 'Primo post!'}
        )
        assert resp.status_code == 200

        # 2) Alice commenta
        resp = client.post(
            f'/comment/{post_id}',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'text': 'Commento iniziale'}
        )
        assert resp.status_code == 200

        # 3) Bob vota il post
        resp = client.post(
            f'/vote/{post_id}',
            headers={'Authorization': f'Bearer {bob_token}'},
            json={'candidate': 'alice'}
        )
        assert resp.status_code == 200

        # 4) Bob avvia il duello
        resp = client.post(
            f'/start_duel/{post_id}',
            headers={'Authorization': f'Bearer {bob_token}'}
        )
        assert resp.status_code == 200

        # 5) Alice vota nuovamente
        resp = client.post(
            f'/vote/{post_id}',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'candidate': 'alice'}
        )
        assert resp.status_code == 200

    # 6) Verifica che Alice abbia guadagnato il badge "Consistent Debater"
    resp = client.get(
        '/profile',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert resp.status_code == 200
    badges = resp.get_json()['badges']
    assert 'Consistent Debater' in badges
