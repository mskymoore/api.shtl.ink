import os
from requests import post
import pyperclip


def get_token(username, password, otp=None, clipboard=False):
    _oidc_issuer = "OIDC_ISSUER"
    _client_id = "CLIENT_ID"
    _client_secret = "CLIENT_SECRET"

    oidc_issuer = os.environ.get(_oidc_issuer, "https://iam.rwx.dev/realms/rwxdev")
    client_id = os.environ.get(_client_id, "api.shtl.ink")
    client_secret = os.environ.get(_client_secret, None)

    missing_vars = [
        name
        for name, value in [
            ("CLIENT_SECRET", client_secret),
            ("CLIENT_ID", client_id),
            ("OIDC_ISSUER", oidc_issuer),
        ]
        if not value
    ]

    if missing_vars:
        raise Exception(
            f"{', '.join(missing_vars)} {'is' if len(missing_vars) == 1 else 'are'} not in the environment."
        )

    token_url = f"https://{oidc_issuer}/protocol/openid-connect/token"

    data = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "client_id": client_id,
        "client_secret": client_secret,
    }

    if otp:
        data["otp"] = otp

    token_response = post(
        token_url,
        data=data,
        timeout=5,
    )

    if token_response.status_code == 200:
        token_data = token_response.json()
        access_token = token_data["access_token"]
        if clipboard:
            pyperclip.copy(access_token)
            print("Access token copied to clipboard.")
        return access_token
    else:
        print(f"Failed to obtain token: {token_response.text}")
        return None
