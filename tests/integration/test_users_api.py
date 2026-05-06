import jwt


def test_create_user_returns_201(client):
    response = client.post(
        "/api/users",
        json={
            "email": "user@example.com",
            "password": "Abcdef1!",
            "name": "User Example",
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 2,
        "email": "user@example.com",
        "name": "User Example",
    }


def test_create_user_with_invalid_password_returns_400(client):
    response = client.post(
        "/api/users",
        json={
            "email": "user@example.com",
            "password": "weak",
            "name": "User Example",
        },
    )

    assert response.status_code == 400
    assert response.json()["message"] == "Validation failed"


def test_list_users_is_public(client):
    response = client.get("/api/users")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "email": "admin@admin.com",
            "name": "Auth Server Administrator",
        }
    ]


def test_invalid_sort_direction_returns_400(client):
    response = client.get("/api/users?sortDir=SIDEWAYS")

    assert response.status_code == 400
    assert response.json()["message"] == "Invalid sort dir"


def test_login_returns_compatible_jwt_payload(client):
    response = client.post(
        "/api/users/login",
        json={
            "email": "admin@admin.com",
            "password": "admin",
        },
    )

    assert response.status_code == 200
    payload = jwt.decode(
        response.json()["token"],
        "test-secret-with-at-least-thirty-two-characters",
        algorithms=["HS256"],
        issuer="PUCPR AuthServer",
    )
    assert payload["sub"] == "1"
    assert payload["user"] == {
        "id": 1,
        "name": "Auth Server Administrator",
        "roles": ["ADMIN"],
    }


def test_common_user_cannot_patch_another_user(client):
    create_response = client.post(
        "/api/users",
        json={
            "email": "user@example.com",
            "password": "Abcdef1!",
            "name": "User Example",
        },
    )
    another_response = client.post(
        "/api/users",
        json={
            "email": "other@example.com",
            "password": "Abcdef1!",
            "name": "Other User",
        },
    )
    login_response = client.post(
        "/api/users/login",
        json={
            "email": "user@example.com",
            "password": "Abcdef1!",
        },
    )

    user_id = create_response.json()["id"]
    another_id = another_response.json()["id"]
    token = login_response.json()["token"]

    response = client.patch(
        f"/api/users/{another_id}",
        json={"name": "New Name"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert user_id != another_id
    assert response.status_code == 403
    assert response.json()["message"] == "Update is not allowed"


def test_patch_same_name_returns_204(client):
    login_response = client.post(
        "/api/users/login",
        json={
            "email": "admin@admin.com",
            "password": "admin",
        },
    )
    token = login_response.json()["token"]

    response = client.patch(
        "/api/users/1",
        json={"name": "Auth Server Administrator"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204
    assert response.content == b""


def test_role_filter_is_case_sensitive(client):
    login_response = client.post(
        "/api/users/login",
        json={
            "email": "admin@admin.com",
            "password": "admin",
        },
    )
    token = login_response.json()["token"]

    client.post(
        "/api/users",
        json={
            "email": "user@example.com",
            "password": "Abcdef1!",
            "name": "User Example",
        },
    )
    client.put(
        "/api/users/2/roles/premium",
        headers={"Authorization": f"Bearer {token}"},
    )

    uppercase_response = client.get("/api/users?role=PREMIUM")
    lowercase_response = client.get("/api/users?role=premium")

    assert uppercase_response.status_code == 200
    assert uppercase_response.json() == [
        {
            "id": 2,
            "email": "user@example.com",
            "name": "User Example",
        }
    ]
    assert lowercase_response.status_code == 200
    assert lowercase_response.json() == []
