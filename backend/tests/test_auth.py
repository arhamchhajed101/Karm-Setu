from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_login_admin(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@karmsetu.in", "password": "Password123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "cooperative_admin"
    assert data["email"] == "admin@karmsetu.in"


def test_login_worker(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "worker@karmsetu.in", "password": "Password123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "worker"


def test_login_customer(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "customer@karmsetu.in", "password": "Password123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "customer"


def test_login_invalid_password(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@karmsetu.in", "password": "WrongPassword!"},
    )
    assert response.status_code == 401


def test_get_me_authenticated(client: TestClient):
    # First login
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "customer@karmsetu.in", "password": "Password123!"},
    )
    token = login_res.json()["access_token"]

    # Call /me
    res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "customer@karmsetu.in"
    assert "customer_profile" in data
