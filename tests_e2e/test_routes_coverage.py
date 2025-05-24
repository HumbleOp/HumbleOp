def test_results_invalid_id(client, alice_token):
    rv = client.get("/results/invalid123", headers={"Authorization": f"Bearer {alice_token}"})
    assert rv.status_code == 404


def test_flag_invalid_id(client, alice_token):
    rv = client.post("/flag/invalid999", headers={"Authorization": f"Bearer {alice_token}"})
    assert rv.status_code == 404


def test_like_invalid_id(client, alice_token):
    rv = client.post("/like/invalid999", headers={"Authorization": f"Bearer {alice_token}"})
    assert rv.status_code == 404


def test_comment_missing_body(client, unique_post_id, alice_token):
    client.post(f"/create_post/{unique_post_id}", headers={"Authorization": f"Bearer {alice_token}"}, json={"body": "test"})
    rv = client.post(f"/comment/{unique_post_id}", headers={"Authorization": f"Bearer {alice_token}"}, json={})
    assert rv.status_code == 400


def test_upload_invalid_file_type(client, alice_token):
    file_data = {
        'avatar': ('filename.txt', b'invalid content', 'text/plain')
    }
    rv = client.post("/upload_avatar", headers={"Authorization": f"Bearer {alice_token}"}, files=file_data)
    assert rv.status_code == 400


def test_upload_no_file(client, alice_token):
    rv = client.post("/upload_avatar", headers={"Authorization": f"Bearer {alice_token}"})
    assert rv.status_code == 400
