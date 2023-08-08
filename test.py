#!.venv/bin/python3
import os
from dotenv import load_dotenv
from requests import get, post
from decode import decode_token
import json


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

    key_url = "https://iam.rwx.dev/realms/rwxdev/protocol/openid-connect/certs"

    # print(json.dumps(decode_token(access_token, key_url, "api.shtl.ink"), indent=4))
    refresh_token = response_json["refresh_token"]

    # url = "https://iam.rwx.dev/realms/rwxdev/protocol/openid-connect/certs"
    # public_key_pem = get_public_key_pem(url)
    # print("checking expiration of access token...")
    # decode_token(access_token, public_key_pem, "api.shtl.ink")
    # print("checking expiration of refresh token...")
    # decode_token(refresh_token, public_key_pem, "api.shtl.ink")

    print("Getting all short codes...")
    if access_token:
        response = get(
            "http://localhost:8000/all_short_codes",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        print(response.json())

    print("Creating short code...")
    if access_token:
        response = post(
            "http://localhost:8000/create_short_code",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"url": "https://www.reddit.com"},
        )
        print(response.json())

    # print("Refreshing token...")
    # response = post(
    #     "http://localhost:8000/auth/refresh",
    #     headers={"Content-Type": "application/json"},
    #     json={"refresh_token": refresh_token},
    #     timeout=5,
    # )
    # response_json = response.json()
    # access_token = response_json["access_token"]
    # refresh_token = response_json["refresh_token"]

    # print("Getting all short codes...")
    # if access_token:
    #     response = get(
    #         "http://localhost:8000/all_short_codes",
    #         headers={"Authorization": f"Bearer {access_token}"},
    #     )
    #     print(response.json())
