from typing import Dict

from fastapi.testclient import TestClient


def create_user(client: TestClient, user_1: Dict):
    response = client.post("/users", json=user_1)
    assert response.status_code == 200

    return response


def login_user(client: TestClient, user_1: Dict) -> str:
    response = client.post(
        "/token",
        data={
            "username": user_1["email"],
            "password": user_1["password"],
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

    return response.json()["access_token"]
