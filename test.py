#!.venv/bin/python3
import os
from requests import get
from dotenv import load_dotenv
from requests import get, post

load_dotenv()

if __name__ == "__main__":
    username = os.environ.get("TEST_USER")
    password = os.environ.get("TEST_PASS")

    print("Requesting token...")
    response = post(
        "http://localhost:8000/auth",
        headers={"Content-Type": "application/json"},
        json={"username": username, "password": password},
        timeout=5,
    )

    response_json = response.json()
    access_token = response_json["access_token"]
    refresh_token = response_json["refresh_token"]

    print("Getting all short codes...")
    if access_token:
        for i in range(10):
            response = get(
                "http://localhost:8000/all_short_codes",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            print(response.json())

    print("Refreshing token...")
    response = post(
        "http://localhost:8000/auth/refresh",
        headers={"Content-Type": "application/json"},
        json={"refresh_token": refresh_token},
        timeout=5,
    )
    response_json = response.json()
    access_token = response_json["access_token"]
    refresh_token = response_json["refresh_token"]

    print("Getting all short codes...")
    if access_token:
        for i in range(10):
            response = get(
                "http://localhost:8000/all_short_codes",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            print(response.json())
