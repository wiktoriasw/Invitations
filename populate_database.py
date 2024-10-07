import json

import requests

with open("seed/users.json", "r") as f:
    users = json.load(f)

with open("seed/events.json", "r") as f:
    events = json.load(f)

with open("seed/guests.json", "r") as f:
    guests = json.load(f)


for user in users:
    r = requests.post(
        "http://127.0.0.1:8000/users",
        json=user,
        headers={"Content-Type": "application/json"},
    )

for i, user in enumerate(users):
    r = requests.post(
        "http://127.0.0.1:8000/token",
        data={
            "username": user["email"],
            "password": user["password"],
        },
    )

    token = r.json()["access_token"]

    r = requests.post(
        "http://127.0.0.1:8000/events",
        json=events[i],
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )

    event_uuid = r.json()["uuid"]
    # print(type(event_uuid))
    # print(guests[i])
    guests[i]["event_uuid"] = event_uuid

    r = requests.post(
        "http://127.0.0.1:8000/guests",
        json=guests[i],
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )
    print(r.status_code, r.text)
