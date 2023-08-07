#!.venv/bin/python3
import os, jwt, base64
from requests import get
from dotenv import load_dotenv
from requests import get, post
from datetime import datetime, timezone
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

load_dotenv()


def get_public_key_pem(url):
    response = get(url)
    jwks = response.json()
    for key in jwks["keys"]:
        if key["alg"] == "RS256" and key["use"] == "sig":
            n = int.from_bytes(
                base64.urlsafe_b64decode(key["n"] + "=="), byteorder="big"
            )
            e = int.from_bytes(
                base64.urlsafe_b64decode(key["e"] + "=="), byteorder="big"
            )
            public_key = rsa.RSAPublicNumbers(e, n).public_key(default_backend())
            pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            return pem.decode("utf-8")
    return None


def decode_token(token, public_key_pem, audience):
    try:
        # Decode the token without verification if no secret key is provided
        decoded_token = jwt.decode(
            token, public_key_pem, audience=audience, algorithms=["RS256"]
        )

        # Get the expiration time (exp claim) from the token
        exp_timestamp = decoded_token.get("exp")

        if exp_timestamp:
            # Convert the timestamp to a human-readable format
            expiration_date = datetime.utcfromtimestamp(exp_timestamp).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            utc_dt = datetime.utcfromtimestamp(exp_timestamp).replace(
                tzinfo=timezone.utc
            )
            local_dt = datetime.fromtimestamp(exp_timestamp)

            expiration_date = local_dt.strftime("%Y-%m-%d %H:%M:%S")

            print(f"Token will expire at {expiration_date}")
            return expiration_date
        else:
            print("Expiration time not found in token.")
            return None
    except jwt.ExpiredSignatureError:
        print("Token has expired.")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: \n{e}")
        return None


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

    url = "https://iam.rwx.dev/realms/rwxdev/protocol/openid-connect/certs"
    public_key_pem = get_public_key_pem(url)
    print("checking expiration of access token...")
    decode_token(access_token, public_key_pem, "api.shtl.ink")
    # print("checking expiration of refresh token...")
    # decode_token(refresh_token, public_key_pem, "api.shtl.ink")

    print("Getting all short codes...")
    if access_token:
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
        response = get(
            "http://localhost:8000/all_short_codes",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        print(response.json())
