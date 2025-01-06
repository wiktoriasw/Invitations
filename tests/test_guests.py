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
    "decision_deadline": "2020-11-28T12:00:00",
}

event_2 = {
    "name": "Kolacja \u015awi\u0105teczna Firmowa",
    "description": "Wigilijne spotkanie z zespo\u0142em",
    "start_time": "2024-12-20T18:00:00",
    "location": "Krak\u00f3w",
    "menu": "polskie;wloskie",
    "decision_deadline": "2050-11-28T12:00:00",
}

guest_1 = {
    "name": "Karolina",
    "surname": "Kowalska",
    "email": "karkowal@gmail.com",
    "phone": "+48765456384",
    "has_companion": True,
}

guest_answer_1 = {
    "answer": True,
    "menu": "Wegetariańskie",
}

guest_answer_2 = {
    "answer": True,
    "menu": "polskie",
}

companion_answer = {
    "answer": True,
    "menu": "polskie",
    "comments": "string",
    "name": "Zosia",
    "surname": "Samosia",
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


def test_different_user_delete_guests():
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


def test_different_user_add_guests():
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

    assert response.status_code == 200
    assert len(response.json()) == 0


def test_add_guest_to_event():
    test_utils.create_user(client, user_1)
    user1_token = test_utils.login_user(client, user_1)
    response = test_utils.create_event(client, event_1, user1_token)

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


def test_different_user_add_guest_for_not_their_event():
    test_utils.create_user(client, user_1)
    user1_token = test_utils.login_user(client, user_1)

    test_utils.create_user(client, user_2)
    user2_token = test_utils.login_user(client, user_2)
    response = test_utils.create_event(client, event_2, user2_token)

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

    assert response.status_code == 401


def test_get_guest_by_uuid_from_event():
    test_utils.create_user(client, user_1)
    user1_token = test_utils.login_user(client, user_1)
    response = test_utils.create_event(client, event_1, user1_token)

    event_uuid = response.json()["uuid"]
    assert event_uuid is not None

    guest_1["event_uuid"] = event_uuid

    response = test_utils.add_guest_to_event(client, guest_1, user1_token)
    guest_uuid = response.json()["uuid"]

    response = client.get(
        f"/guests/{guest_uuid}",
    )

    assert response.status_code == 200

    response_data = response.json()
    assert response_data["uuid"] == guest_uuid
    assert response_data["name"] == guest_1["name"]


def test_update_guest_answer_before_deadline():
    test_utils.create_user(client, user_1)
    user1_token = test_utils.login_user(client, user_1)
    response = test_utils.create_event(client, event_2, user1_token)

    event_uuid = response.json()["uuid"]
    assert event_uuid is not None

    event_decision_deadline = response.json()["decision_deadline"]
    assert event_decision_deadline is not None

    guest_1["event_uuid"] = event_uuid

    response = test_utils.add_guest_to_event(client, guest_1, user1_token)
    guest_uuid = response.json()["uuid"]

    response = client.post(
        f"/guests/{guest_uuid}/answer",
        json=guest_answer_2,
    )

    assert response.status_code == 200


def test_guest_cannot_update_answer_after_deadline():
    test_utils.create_user(client, user_1)
    user1_token = test_utils.login_user(client, user_1)
    response = test_utils.create_event(client, event_1, user1_token)

    event_uuid = response.json()["uuid"]
    assert event_uuid is not None

    event_decision_deadline = response.json()["decision_deadline"]
    assert event_decision_deadline is not None

    guest_1["event_uuid"] = event_uuid

    response = test_utils.add_guest_to_event(client, guest_1, user1_token)
    guest_uuid = response.json()["uuid"]

    response = client.post(
        f"/guests/{guest_uuid}/answer",
        json=guest_answer_1,
    )

    assert response.status_code == 406


def test_guest_can_update_companion_answer_before_deadline():
    test_utils.create_user(client, user_1)
    user1_token = test_utils.login_user(client, user_1)
    response = test_utils.create_event(client, event_2, user1_token)

    event_uuid = response.json()["uuid"]
    assert event_uuid is not None

    event_decision_deadline = response.json()["decision_deadline"]
    assert event_decision_deadline is not None

    guest_1["event_uuid"] = event_uuid

    response = test_utils.add_guest_to_event(client, guest_1, user1_token)

    guest_uuid = response.json()["uuid"]
    assert guest_uuid is not None

    response = client.post(
        f"/guests/{guest_uuid}/answer",
        json=guest_answer_2,
    )
    companion_uuid = response.json()["companion_uuid"]
    assert companion_uuid is not None

    response = client.post(
        f"/guests/{companion_uuid}/companion_answer", json=companion_answer
    )
    assert response.status_code == 200


def test_guest_cannot_update_companion_answer_after_deadline():
    pass


# gość może zupadować odp dla kompaniona
# gość nie moze zupdejtowac odp dla kompaniona po terminie

# gość nie może najpierw zaupdatować odpowiedzi dla kompaniona potem dla siebie
# jeśli odp goscia to false, gosc nie moze dac odp za kompaniona
# jesli gośc nie ma companiona to nie moze zupdatować jego odpowiedzi
# jesli gośc daje answer false to nie musi podawać menu?
# read guests dziala
