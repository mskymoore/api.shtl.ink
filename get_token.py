import os
from requests import post
from dotenv import load_dotenv

load_dotenv()


_oidc_audience = "OIDC_AUDIENCE"
_oidc_issuer = "OIDC_ISSUER"
_client_id = "CLIENT_ID"
_client_secret = "CLIENT_SECRET"

oidc_audience = os.environ.get(_oidc_audience, "api.shtl.ink")
oidc_issuer = os.environ.get(_oidc_issuer, "https://iam.rwx.dev/realms/rwxdev")
client_id = os.environ.get(_client_id, "api.shtl.ink")
client_secret = os.environ.get(_client_secret, None)

token_url = f"https://{oidc_issuer}/protocol/openid-connect/token"

token_response = post(
    token_url,
    data={
        "grant_type": "password",
        "username": os.environ.get("TEST_USER"),
        "password": os.environ.get("TEST_PASS")
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
    print(f"Access token obtained: {access_token}")
else:
    print(f"Failed to obtain token: {token_response.text}")
