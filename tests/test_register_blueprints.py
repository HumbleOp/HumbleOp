<<<<<<< HEAD
from flask import Flask
from app.routes import register_blueprints
=======
import sys
import os
from flask import Flask
from app.routes import register_blueprints
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))
>>>>>>> bfa9cd8 (update)

def test_register_blueprints():
    app = Flask(__name__)
    register_blueprints(app)

    # Assert that all blueprints are registered
<<<<<<< HEAD
    assert "/auth" in app.blueprints
    assert "/posts" in app.blueprints
    assert "/comments" in app.blueprints
    assert "/votes" in app.blueprints
    assert "/interactions" in app.blueprints
    assert "/profile" in app.blueprints
=======
    assert "auth" in app.blueprints
    assert "posts" in app.blueprints
    assert "comments" in app.blueprints
    assert "votes" in app.blueprints
    assert "interactions" in app.blueprints
    assert "profile" in app.blueprints
>>>>>>> bfa9cd8 (update)
