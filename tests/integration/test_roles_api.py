def login_as_admin(client) -> str:
    response = client.post(
        "/api/users/login",
        json={
            "email": "admin@admin.com",
            "password": "admin",
        },
    )
    return response.json()["token"]


def test_admin_can_create_role(client):
    token = login_as_admin(client)

    response = client.post(
        "/api/roles",
        json={"name": "gold", "description": "Gold tier"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    assert response.json() == {
        "name": "GOLD",
        "description": "Gold tier",
    }


def test_non_admin_cannot_access_roles(client):
    client.post(
        "/api/users",
        json={
            "email": "user@example.com",
            "password": "Abcdef1!",
            "name": "User Example",
        },
    )
    login_response = client.post(
        "/api/users/login",
        json={
            "email": "user@example.com",
            "password": "Abcdef1!",
        },
    )
    token = login_response.json()["token"]

    response = client.get("/api/roles", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
    assert response.json()["message"] == "Admin role is required"


def test_admin_can_grant_role_and_duplicate_grant_returns_204(client):
    token = login_as_admin(client)
    client.post(
        "/api/users",
        json={
            "email": "user@example.com",
            "password": "Abcdef1!",
            "name": "User Example",
        },
    )

    first_response = client.put(
        "/api/users/2/roles/premium",
        headers={"Authorization": f"Bearer {token}"},
    )
    second_response = client.put(
        "/api/users/2/roles/PREMIUM",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 204


def test_cannot_delete_last_admin(client):
    token = login_as_admin(client)

    response = client.delete("/api/users/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 400
    assert response.json()["message"] == "Cannot delete the last admin"
