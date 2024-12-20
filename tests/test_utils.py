from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from ..crud import users


def create_user(client: TestClient, user: Dict):
    response = client.post("/users", json=user)
    assert response.status_code == 200

    return response


def create_admin(db: Session, client: TestClient, user: Dict):
    response = create_user(client, user)
    users.change_user_role(db, "admin", response.json()["email"])


def login_user(client: TestClient, user: Dict) -> str:
    response = client.post(
        "/token",
        data={
            "username": user["email"],
            "password": user["password"],
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

    return response.json()["access_token"]


def create_event(client: TestClient, event: Dict, token: str):
    response = client.post(
        "/events",
        json=event,
        headers={
            "Authorization": f"Bearer {token}",
        },
    )
    assert response.status_code == 200

    assert response.json()["name"] == event["name"]
    assert response.json()["description"] == event["description"]

    return response
