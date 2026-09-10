def test_signup_login_and_protected_route(client):
    signup = client.post("/auth/signup", json={"email": "user@example.com", "password": "password123"})
    assert signup.status_code == 201
    assert signup.json()["email"] == "user@example.com"

    login = client.post("/auth/login", data={"username": "user@example.com", "password": "password123"})
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"

    assert client.get("/products").status_code == 401


def test_duplicate_signup_is_conflict(client):
    payload = {"email": "same@example.com", "password": "password123"}
    assert client.post("/auth/signup", json=payload).status_code == 201
    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 409


def test_user_can_disable_email_reminders(client, auth_headers):
    initial = client.get("/auth/me/reminders", headers=auth_headers)
    assert initial.status_code == 200
    assert initial.json()["reminder_email_enabled"] is True

    updated = client.patch(
        "/auth/me/reminders",
        headers=auth_headers,
        json={"reminder_email_enabled": False},
    )
    assert updated.status_code == 200
    assert updated.json()["reminder_email_enabled"] is False
