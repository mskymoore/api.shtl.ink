import jwt, base64
from requests import get
from datetime import datetime, timezone
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


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


def decode_token(token, key_url, audience):
    public_key_pem = get_public_key_pem(key_url)
    try:
        # Decode the token without verification if no secret key is provided
        decoded_token = jwt.decode(
            token, public_key_pem, audience=audience, algorithms=["RS256"]
        )
        return decoded_token
    except jwt.ExpiredSignatureError:
        print("Token has expired.")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: \n{e}")
        return None


def get_token_expiration(decoded_token):
    # Get the expiration time (exp claim) from the token
    exp_timestamp = decoded_token.get("exp")

    if exp_timestamp:
        # Convert the timestamp to a human-readable format
        expiration_date = datetime.utcfromtimestamp(exp_timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # utc_dt = datetime.utcfromtimestamp(exp_timestamp).replace(tzinfo=timezone.utc)
        local_dt = datetime.fromtimestamp(exp_timestamp)

        expiration_date = local_dt.strftime("%Y-%m-%d %H:%M:%S")

        print(f"Token will expire at {expiration_date}")
        return expiration_date
    else:
        print("Expiration time not found in token.")
        return None
