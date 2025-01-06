import pytest
from fastapi.testclient import TestClient

from ..configuration import settings
from . import test_utils

settings.sqlalchemy_database_url = "sqlite:///./sql_app_test.db"

from ..main import app  # noqa: E402

client = TestClient(app)

user_1 = {"email": "test_user", "password": "123"}
user_2 = {"email": "test_user_2", "password": "456"}

event_1 = {
    "name": "Spotkanie Biznesowe z Klientem",
    "description": "Om\u00f3wienie warunk\u00f3w wsp\u00f3\u0142pracy w restauracji",
    "start_time": "2024-12-05T14:00:00",
    "location": "Warszawa",
    "menu": "Wegetariańskie;Mięsne",
    "decision_deadline": "2025-11-28T12:00:00",
}

guests = [
    {
        "name": "Karolina",
        "surname": "Kowalska",
        "email": "karkowal@gmail.com",
        "phone": "+48765456384",
        "has_companion": True,
    },
    {
        "name": "Micha\u0142",
        "surname": "Nowak",
        "email": "michalnowak@gmail.com",
        "phone": "+48783467582",
    },
]

guest_1 = {
    "name": "Karolina",
    "surname": "Kowalska",
    "email": "karkowal@gmail.com",
    "phone": "+48765456384",
}

event_modify = {
    "name": "Kolacja z klientem",
    "description": "Umowa i warunki",
}

guest_answer = {
    "answer": True,
    "menu": "Wegetariańskie",
}


@pytest.fixture(scope="function", autouse=True)
def clean_up():
    client.post("/reset_tables")


def test_create_event():
    test_utils.create_user(client=client, user=user_1)
    token = test_utils.login_user(client=client, user=user_1)
    test_utils.create_event(client=client, event=event_1, token=token)


def test_delete_event():
    test_utils.create_user(client=client, user=user_1)
    token = test_utils.login_user(client=client, user=user_1)
    response = test_utils.create_event(client=client, event=event_1, token=token)

    event_uuid = response.json()["uuid"]
    assert event_uuid is not None

    response = client.delete(
        f"events/{event_uuid}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    response = client.get(
        f"/events/{event_uuid}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 404


def test_modify_event():
    test_utils.create_user(client=client, user=user_1)
    token = test_utils.login_user(client=client, user=user_1)
    response = test_utils.create_event(client=client, event=event_1, token=token)

    event_data = response.json()

    event_uuid = event_data["uuid"]
    assert event_uuid is not None

    updated_data = {
        "name": "Updated Event Name",
        "description": event_data["description"],
        "start_time": "2024-12-15T12:00:00",
        "location": event_data["location"],
        "menu": "Updated Menu",
        "decision_deadline": event_data["decision_deadline"],
    }

    response = client.put(
        f"events/{event_uuid}",
        json=updated_data,
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    updated_response = response.json()

    assert updated_response["name"] == updated_data["name"]
    assert updated_response["start_time"] == updated_data["start_time"]
    assert updated_response["menu"] == updated_data["menu"]

    assert updated_response["description"] == event_data["description"]
    assert updated_response["location"] == event_data["location"]
    assert updated_response["decision_deadline"] == event_data["decision_deadline"]


def test_different_user_delete_event():
    test_utils.create_user(client=client, user=user_1)
    user1_token = test_utils.login_user(client=client, user=user_1)
    response = test_utils.create_event(client=client, event=event_1, token=user1_token)

    event_uuid = response.json()["uuid"]
    assert event_uuid is not None

    assert test_utils.create_user(client=client, user=user_2)
    user2_token = test_utils.login_user(client=client, user=user_2)

    response = client.delete(
        f"/events/{event_uuid}",
        headers={
            "Authorization": f"Bearer {user2_token}",
        },
    )

    assert response.status_code == 404

    response = client.get(
        f"/events/{event_uuid}",
    )

    assert response.status_code == 200


def test_different_user_modify_event():
    test_utils.create_user(client=client, user=user_1)
    user1_token = test_utils.login_user(client=client, user=user_1)

    response = test_utils.create_event(client=client, event=event_1, token=user1_token)
    event_uuid = response.json()["uuid"]
    assert event_uuid is not None

    test_utils.create_user(client, user_2)
    user2_token = test_utils.login_user(client=client, user=user_2)

    response = client.put(
        f"/events/{event_uuid}",
        json=event_modify,
        headers={
            "Authorization": f"Bearer {user2_token}",
        },
    )
    assert response.status_code == 404

    response = client.get(f"/events/{event_uuid}")

    assert response.json()["name"] == event_1["name"]
    assert response.json()["description"] == event_1["description"]


def test_get_guests_from_event():
    test_utils.create_user(client=client, user=user_1)
    token = test_utils.login_user(client=client, user=user_1)
    response = test_utils.create_event(client=client, event=event_1, token=token)

    event_uuid = response.json()["uuid"]
    assert event_uuid is not None

    test_utils.create_guest(client, guest_1, event_uuid, token)

    response = client.get(
        f"/events/{event_uuid}/guests",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_different_user_get_guests_from_event():
    test_utils.create_user(client=client, user=user_1)
    user1_token = test_utils.login_user(client=client, user=user_1)
    response = test_utils.create_event(client=client, event=event_1, token=user1_token)

    event_uuid = response.json()["uuid"]
    assert event_uuid is not None

    test_utils.create_guest(client, guest_1, event_uuid, user1_token)

    test_utils.create_user(client, user_2)
    user2_token = test_utils.login_user(client=client, user=user_2)

    response = client.get(
        f"/events/{event_uuid}/guests",
        headers={
            "Authorization": f"Bearer {user2_token}",
        },
    )

    assert response.status_code == 401


def test_get_event_stats():
    test_utils.create_user(client=client, user=user_1)

    token = test_utils.login_user(client=client, user=user_1)
    response = test_utils.create_event(client=client, event=event_1, token=token)

    event_uuid = response.json()["uuid"]
    assert event_uuid is not None

    guest = test_utils.create_guest(client, guest_1, event_uuid, token)
    guest_uuid = guest.json()["uuid"]
    assert guest_uuid is not None

    response = client.post(f"/guests/{guest_uuid}/answer", json=guest_answer)
    assert response.status_code == 200

    response = client.get(
        f"/events/{event_uuid}/stats",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    stats = response.json()

    assert "sum_true" in stats
    assert stats["sum_true"] == 1

    assert "sum_false" in stats
    assert stats["sum_false"] == 0

    assert "sum_unkown" in stats

    assert "menu_answers" in stats
    assert stats["menu_answers"]["Wegetariańskie"] == 1


def test_different_user_get_event_stats():
    test_utils.create_user(client=client, user=user_1)
    user1_token = test_utils.login_user(client=client, user=user_1)
    response = test_utils.create_event(client=client, event=event_1, token=user1_token)

    event_uuid = response.json()["uuid"]
    assert event_uuid is not None

    test_utils.create_guest(client, guest_1, event_uuid, user1_token)

    test_utils.create_user(client, user_2)
    user2_token = test_utils.login_user(client=client, user=user_2)

    guest = test_utils.create_guest(client, guest_1, event_uuid, user1_token)
    guest_uuid = guest.json()["uuid"]
    assert guest_uuid is not None

    response = client.post(f"/guests/{guest_uuid}/answer", json=guest_answer)
    assert response.status_code == 200

    response = client.get(
        f"/events/{event_uuid}/stats",
        headers={
            "Authorization": f"Bearer {user2_token}",
        },
    )

    assert response.status_code == 401


def get_event_by_uuid():
    test_utils.create_user(client=client, user=user_1)
    user1_token = test_utils.login_user(client=client, user=user_1)
    response = test_utils.create_event(client=client, event=event_1, token=user1_token)
    event_uuid = response.json()["uuid"]
    assert event_uuid is not None

    response = client.get(f"/events/{event_uuid}")

    assert response.status_code == 200


def get_events():
    test_utils.create_user(client=client, user=user_1)
    token = test_utils.login_user(client=client, user=user_1)
    test_utils.create_event(client=client, event=event_1, token=token)

    response = client.get("/events")
    assert response.status_code == 200

    events = response.json()
    assert len(events) == 1
    assert events[0]["name"] == event_1["name"]
