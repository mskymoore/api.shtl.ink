from requests import post


def get_permissions(access_token, oidc_issuer, client_id):
    token_url = f"https://{oidc_issuer}/protocol/openid-connect/token"

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    payload = {
        "grant_type": "urn:ietf:params:oauth:grant-type:uma-ticket",
        "audience": client_id,
        # "permission": [
        #     "/all_short_codes#get:all_short_codes",
        #     "/create_short_code#post:create_short_code",
        # ],
    }

    permission_response = post(token_url, headers=headers, data=payload, timeout=5)

    return permission_response


def get_oidc_token(username, password, oidc_issuer, client_id, client_secret, otp=None):
    token_url = f"https://{oidc_issuer}/protocol/openid-connect/token"

    data = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "openid",
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
        refresh_token = token_data["refresh_token"]

        permissions = get_permissions(access_token, oidc_issuer, client_id)

        if permissions.status_code == 200:
            permissions_json = permissions.json()
            access_token, refresh_token = (
                permissions_json["access_token"],
                permissions_json["refresh_token"],
            )

        return access_token, refresh_token
    else:
        print(f"Failed to obtain token: {token_response.text}")
        return None


def refresh_oidc_token(oidc_issuer, client_id, client_secret, refresh_token):
    token_url = f"https://{oidc_issuer}/protocol/openid-connect/token"

    data = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
    }

    token_response = post(
        token_url,
        data=data,
        timeout=5,
    )

    if token_response.status_code == 200:
        token_data = token_response.json()
        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]
        return access_token, refresh_token
    else:
        print(f"Failed to refresh token: {token_response.text}")
        return None
