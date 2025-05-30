
def test_comment_missing_body(client, unique_post_id, alice_token):
    client.post(f"/create_post/{unique_post_id}", headers={"Authorization": f"Bearer {alice_token}"}, json={"body": "test"})
    client.post("/register", json={"username": "cov_cm", "password": "x", "email": "cov_cm@example.com"})
    cov_token = client.post("/login", json={"username": "cov_cm", "password": "x"}).json()["access_token"]
    rv = client.post(f"/comment/{unique_post_id}", headers={"Authorization": f"Bearer {cov_token}"}, json={})
    assert rv.status_code == 400
