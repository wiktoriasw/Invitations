import requests
import json

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

    r = requests.post(
        "http://127.0.0.1:8000/guests",
        json=guests[i],
        headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
    )
    # dodawanie 2 gości - moga byc ci sami do kazdego z eventow
    print(r.status_code)
