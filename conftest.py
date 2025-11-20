import pytest
from config import create_app, db

@pytest.fixture()
def app():
    from app import app
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()
