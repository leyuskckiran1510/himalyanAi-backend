import pytest
from flask import Flask
from flask_jwt_extended import decode_token
from app import create_app, db
from app.models import User, Summary


@pytest.fixture
def client():
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # In-memory DB for testing
    app.config["JWT_SECRET_KEY"] = "test-secret"
    app.config["TESTING"] = True
    app.testing = True

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_authenticate_or_identify_success(client):
    response = client.post("/authenticate_or_identify", json={"hash": "randomhash123"})
    print(response.headers)
    assert response.status_code == 200
    assert "access_token" in response.get_json()


def test_authenticate_or_identify_missing_hash(client):
    response = client.post("/authenticate_or_identify", json={})
    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing hash"}


def test_summarize_success(client):
    # First, authenticate to get token
    auth_resp = client.post("/authenticate_or_identify", json={"hash": "testhash"})
    token = auth_resp.get_json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/summarize", json={"content": "This is test content."}, headers=headers)

    assert response.status_code == 200
    data = response.get_json()
    assert "summary" in data or "notes" in data or "refrences" in data


def test_summarize_missing_auth(client):
    response = client.post("/summarize", json={"content": "Missing token"})
    assert response.status_code == 401  # Unauthorized


def test_fetch_user_history_empty(client):
    # Create user and token
    auth_resp = client.post("/authenticate_or_identify", json={"hash": "history-user"})
    token = auth_resp.get_json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/fetch_user_history", headers=headers)

    assert response.status_code == 200
    assert response.get_json() == []


def test_fetch_user_history_with_entries(client):
    # Create user
    user = User(anon_hash="history-user2")
    db.session.add(user)
    db.session.commit()

    # Add summaries
    db.session.add(
        Summary(user_id=user.id, summary_id="sum1", full_url="http://example.com", site_domain="example.com")
    )
    db.session.commit()

    # Get token
    auth_resp = client.post("/authenticate_or_identify", json={"hash": "history-user2"})
    token = auth_resp.get_json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/fetch_user_history", headers=headers)

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert data[0]["summary_id"] == "sum1"
