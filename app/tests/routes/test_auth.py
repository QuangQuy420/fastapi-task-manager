from fastapi import HTTPException


def test_route_register_success(client, mock_user_service):
    """Test successful user registration."""
    mock_user_service.register.return_value = {
        "id": 1,
        "email": "new@test.com",
        "full_name": "New User",
        "is_active": True,
        "created_at": "2025-12-11T00:00:00",
        "updated_at": "2025-12-11T00:00:00",
    }

    payload = {
        "email": "new@test.com",
        "password": "password123",
        "full_name": "New User",
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new@test.com"
    mock_user_service.register.assert_awaited_once()


def test_route_register_duplicate_email(client, mock_user_service):
    mock_user_service.register.side_effect = HTTPException(
        status_code=400, detail="Email already registered"
    )

    payload = {
        "email": "existing@test.com",
        "password": "password123",
        "full_name": "User",
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 400


def test_route_register_invalid_email(client):
    payload = {"email": "invalid-email", "password": "pwd", "full_name": "User"}
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422


def test_route_login_success(client, mock_user_service):
    mock_user_service.authenticate_and_create_tokens.return_value = (
        "fake_access",
        "fake_refresh",
    )
    form_data = {"username": "user@test.com", "password": "secretpassword"}

    response = client.post("/auth/login", data=form_data)

    assert response.status_code == 200
    assert response.json()["access_token"] == "fake_access"
    assert response.cookies["refresh_token"] == "fake_refresh"


def test_route_login_wrong_password(client, mock_user_service):
    mock_user_service.authenticate_and_create_tokens.side_effect = HTTPException(
        status_code=400, detail="Incorrect email or password"
    )
    form_data = {"username": "user@test.com", "password": "wrongpassword"}
    response = client.post("/auth/login", data=form_data)
    assert response.status_code == 400


def test_route_refresh_success(client, mock_user_service):
    mock_user_service.refresh_tokens.return_value = ("new_access", "new_refresh")
    client.cookies.set("refresh_token", "valid_old_refresh_token")

    response = client.post("/auth/refresh")

    assert response.status_code == 200
    assert response.json()["access_token"] == "new_access"
    mock_user_service.refresh_tokens.assert_awaited_once_with("valid_old_refresh_token")


def test_route_logout_success(client):
    response = client.post("/auth/logout")
    assert response.status_code == 200
