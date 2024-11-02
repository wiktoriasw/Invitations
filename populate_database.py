import json
from tqdm import tqdm
import requests

with open("seed/users.json", "r") as f:
    users = json.load(f)

with open("seed/events.json", "r") as f:
    events = json.load(f)

with open("seed/guests.json", "r") as f:
    guests = json.load(f)


for i, user in tqdm([*enumerate(users)], colour="#50A050"):

    r = requests.post(
        "http://127.0.0.1:8000/users",
        json=user,
        headers={"Content-Type": "application/json"},
    )

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
    guests[i]["event_uuid"] = event_uuid

    r = requests.post(
        "http://127.0.0.1:8000/guests",
        json=guests[i],
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )
