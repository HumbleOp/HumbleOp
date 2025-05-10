def test_authentication_required(client):
    """Test that routes requiring authentication return a 401 error when unauthenticated."""
    response = client.post("/interactions/flag/test_post")
    assert response.status_code == 401
    assert response.json == {"error": "Authentication required"}