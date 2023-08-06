import os
from requests import post
import pyperclip


def get_token(username, password, clipboard=False):
    _oidc_audience = "OIDC_AUDIENCE"
    _oidc_issuer = "OIDC_ISSUER"
    _client_id = "CLIENT_ID"
    _client_secret = "CLIENT_SECRET"

    oidc_issuer = os.environ.get(_oidc_issuer, "https://iam.rwx.dev/realms/rwxdev")
    client_id = os.environ.get(_client_id, "api.shtl.ink")
    client_secret = os.environ.get(_client_secret, None)

    if not client_secret:
        raise Exception("CLIENT_SECRET is not in the environment.")

    token_url = f"https://{oidc_issuer}/protocol/openid-connect/token"

    token_response = post(
        token_url,
        data={
            "grant_type": "password",
            "username": username,
            "password": password,
            # Tempoararily diabled OTP on direct grant auth method
            # "otp": os.environ.get("TEST_OTP"),
            "client_id": client_id,
            "client_secret": client_secret,
        },
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
