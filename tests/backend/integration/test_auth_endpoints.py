import pytest


@pytest.mark.integration
def test_register_login_and_me_flow(client):
    payload = {"login": "alice", "password": "alicepass123"}

    register_response = client.post("/auth/register", json=payload)
    assert register_response.status_code == 201
    assert register_response.json()["login"] == "alice"

    login_response = client.post("/auth/login", json=payload)
    assert login_response.status_code == 200
    token_body = login_response.json()
    assert "access_token" in token_body
    assert "refresh_token" in token_body
    assert token_body["token_type"] == "bearer"

    headers = {"Authorization": f"Bearer {token_body['access_token']}"}
    me_response = client.get("/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["login"] == "alice"


@pytest.mark.integration
def test_refresh_token_flow(client):
    payload = {"login": "bob", "password": "bobpass123"}
    client.post("/auth/register", json=payload)
    login_response = client.post("/auth/login", json=payload)
    refresh_token = login_response.json()["refresh_token"]

    refresh_response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_response.status_code == 200
    refreshed = refresh_response.json()
    assert refreshed["access_token"]
    assert refreshed["refresh_token"]


@pytest.mark.integration
def test_login_validation_error(client):
    response = client.post("/auth/login", json={"login": "x", "password": "123"})
    assert response.status_code == 422
