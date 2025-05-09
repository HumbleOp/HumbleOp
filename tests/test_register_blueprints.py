from flask import Flask
from app.routes import register_blueprints

def test_register_blueprints():
    app = Flask(__name__)
    register_blueprints(app)

    # Assert that all blueprints are registered
    assert "auth" in app.blueprints
    assert "posts" in app.blueprints
    assert "comments" in app.blueprints
    assert "votes" in app.blueprints
    assert "interactions" in app.blueprints
    assert "profile" in app.blueprints