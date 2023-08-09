from requests import post, get
from typing import List, Dict


def create_role_policy(
    access_token: str,
    oidc_issuer: str,
    realm: str,
    client_id: str,
    policy_name: str,
    # {"id": role_name, "required": True}
    roles: Dict[str, str],
) -> Dict:
    url = f"https://{oidc_issuer}/auth/admin/realms/{realm}/clients/{client_id}/authz/resource-server/policy/role"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    data = {"name": policy_name, "roles": roles}
    response = post(url, json=data, headers=headers, timeout=5)
    return response.json()


def create_resource(
    access_token: str,
    oidc_issuer: str,
    realm: str,
    client_id: str,
    resource_name: str,
    uris: List[str],
    # {"name": scope_name}
    scopes: List[str],
) -> Dict:
    url = f"https://{oidc_issuer}/realms/{realm}/authz/protection/resource_set"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    # TODO: enable owner managed access here to fix policy/permission creation
    data = {
        "name": resource_name,
        "uris": uris,
        "resource_scopes": scopes,
    }
    response = post(url, json=data, headers=headers, timeout=5)
    return response.json()


def create_permission(
    access_token: str,
    oidc_issuer: str,
    realm: str,
    permission_name: str,
    permission_description: str,
    resource_id: str,
    roles: List[str],
    scopes: List[str],
) -> Dict:
    url = f"https://{oidc_issuer}/realms/{realm}/authz/protection/resource_set?uri={resource_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    data = {
        "name": permission_name,
        "description": permission_description,
        "roles": roles,
        "scopes": scopes,
    }
    resource_id = get(url, headers=headers, timeout=5).json()[0]
    url = f"https://{oidc_issuer}/realms/{realm}/authz/protection/uma-policy/{resource_id}"
    # TODO: fix - only resources with owner managed access can have policies
    response = post(url, json=data, headers=headers, timeout=5)
    return response.json()


def get_client_access_token(
    oidc_issuer: str, realm: str, client_id: str, client_secret: str
) -> str | None:
    token_url = f"https://{oidc_issuer}/realms/{realm}/protocol/openid-connect/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    response = post(token_url, data=data, timeout=5)
    if response.status_code == 200:
        response_json = response.json()
        return response_json.get("access_token")
    else:
        print(f"Failed to get access_token: {response.text}")
        return None


def init_keycloak_resources(
    oidc_issuer: str, realm: str, client_id: str, client_secret: str
) -> bool:
    access_token = get_client_access_token(oidc_issuer, realm, client_id, client_secret)

    if access_token:
        scope_name = "post:create_custom_short_code"
        resource_name = "/create_custom_short_code"
        uri = "/create_custom_short_code"

        # scope_response = create_scope(
        #     access_token, oidc_issuer, realm, client_id, scope_name
        # )

        resource_response = create_resource(
            access_token,
            oidc_issuer,
            realm,
            client_id,
            resource_name,
            [uri],
            [{"name": scope_name}],
        )

        permission_response = create_permission(
            access_token,
            oidc_issuer,
            realm,
            "create_custom_short_code",
            "Create a custom short code",
            resource_name,
            ["shtl-ink-api"],
            [scope_name],
        )
        return True
    else:
        return False
