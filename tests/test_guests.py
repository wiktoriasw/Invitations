import pytest
from fastapi.testclient import TestClient

from ..configuration import settings
from . import test_utils

settings.sqlalchemy_database_url = "sqlite:///./sql_app_test.db"

from ..main import app

client = TestClient(app)


user_1 = {"email": "test_user", "password": "123"}
user_2 = {"email": "test_user_2", "password": "456"}

event_1 = {
    "name": "Spotkanie Biznesowe z Klientem",
    "description": "Om\u00f3wienie warunk\u00f3w wsp\u00f3\u0142pracy w restauracji",
    "start_time": "2024-12-05T14:00:00",
    "location": "Warszawa",
    "menu": "Wegetariańskie;Mięsne",
    "decision_deadline": "2024-11-28T12:00:00",
}

guest_1 = {
    "name": "Karolina",
    "surname": "Kowalska",
    "email": "karkowal@gmail.com",
    "phone": "+48765456384",
}


@pytest.fixture(scope="function", autouse=True)
def clean_up():
    client.post("/reset_tables")


def test_delete_guest_from_event():
    assert test_utils.create_user(client=client, user=user_1)
    token = test_utils.login_user(client=client, user=user_1)
    response = test_utils.create_event(client=client, event=event_1, token=token)

    event_uuid = response.json()["uuid"]
    guest_1["event_uuid"] = event_uuid

    response = client.post(
        "/guests",
        json=guest_1,
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    guest_uuid = response.json()["uuid"]

    response = client.delete(
        f"/guests/{guest_uuid}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    response = client.get(
        f"/guests/{guest_uuid}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 404


def test_wrong_user_delete_guests():
    test_utils.create_user(client=client, user=user_1)
    user1_token = test_utils.login_user(client=client, user=user_1)
    response = test_utils.create_event(client=client, event=event_1, token=user1_token)
    event_uuid = response.json()["uuid"]
    assert event_uuid is not None
    guest_1["event_uuid"] = event_uuid

    response = client.post(
        "/guests",
        json=guest_1,
        headers={
            "Authorization": f"Bearer {user1_token}",
        },
    )

    assert response.status_code == 200
    guest_uuid = response.json()["uuid"]

    test_utils.create_user(client=client, user=user_2)
    user2_token = test_utils.login_user(client=client, user=user_2)

    response = client.delete(
        f"/guests/{guest_uuid}",
        headers={
            "Authorization": f"Bearer {user2_token}",
        },
    )

    assert response.status_code == 404

    response = client.get(f"/guests/{guest_uuid}")

    assert response.status_code == 200


def test_wrong_user_add_guests():
    test_utils.create_user(client=client, user=user_1)
    user1_token = test_utils.login_user(client=client, user=user_1)

    response = test_utils.create_event(client=client, event=event_1, token=user1_token)
    event_uuid = response.json()["uuid"]
    assert event_uuid is not None
    guest_1["event_uuid"] = event_uuid

    test_utils.create_user(client=client, user=user_2)
    user2_token = test_utils.login_user(client=client, user=user_2)

    response = client.post(
        "/guests",
        json=guest_1,
        headers={
            "Authorization": f"Bearer {user2_token}",
        },
    )

    assert response.status_code == 401

    response = client.get(
        f"/events/{event_uuid}/guests",
        headers={
            "Authorization": f"Bearer {user1_token}",
        },
    )

    assert len(response.json()) == 0
