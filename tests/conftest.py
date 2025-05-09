import pytest
from app.models.models import db
from app import create_app

@pytest.fixture
def app():
    """Setup Flask application for testing."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()  # Create all tables
        yield app
        db.session.remove()
        db.drop_all()  # Drop all tables after tests

@pytest.fixture
def client(app):
    """Provide a test client for the Flask app."""
    return app.test_client()