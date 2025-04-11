import pytest
from flask import Flask, cli
from flask_jwt_extended import decode_token
from app import create_app, db
from app.models import User, Summary


@pytest.fixture
def client():
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # In-memory DB for testing
    app.config["JWT_SECRET_KEY"] = "test-secret"
    app.config["TESTING"] = True
    app.config["url_scheme"] = "https"
    app.testing = True

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_authenticate_or_identify_success(client):
    response = client.post(
        "/api/authenticate_or_identify", json={"hash": "randomhash123"}, base_url="https://localhost"
    )
    assert response.status_code == 200
    assert "access_token" in response.get_json()


def test_authenticate_or_identify_missing_hash(client):
    response = client.post("/api/authenticate_or_identify", json={}, base_url="https://localhost")
    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing hash"}


def test_summarize_success(client):
    # First, authenticate to get token
    auth_resp = client.post("/api/authenticate_or_identify", json={"hash": "testhash"}, base_url="https://localhost")
    token = auth_resp.get_json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/summarize", json={"content": "This is test content."}, headers=headers, base_url="https://localhost"
    )
    print(response.text, response.request.__dict__, response.get_json())
    assert response.status_code == 200, f"Failed with: {response.get_json()}"
    data = response.get_json()
    assert "summary" in data or "notes" in data or "refrences" in data


def test_summarize_missing_auth(client):
    response = client.post("/api/summarize", json={"content": "Missing token"}, base_url="https://localhost")
    assert response.status_code == 401  # Unauthorized


def test_fetch_user_history_empty(client):
    # Create user and token
    auth_resp = client.post(
        "/api/authenticate_or_identify", json={"hash": "history-user"}, base_url="https://localhost"
    )
    token = auth_resp.get_json()["access_token"]
    print(token)

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/fetch_user_history", headers=headers, base_url="https://localhost")

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
    auth_resp = client.post(
        "/api/authenticate_or_identify", json={"hash": "history-user2"}, base_url="https://localhost"
    )
    token = auth_resp.get_json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/fetch_user_history", headers=headers, base_url="https://localhost")

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert data[0]["summary_id"] == "sum1"
