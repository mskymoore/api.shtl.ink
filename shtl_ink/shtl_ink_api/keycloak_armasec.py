from functools import partial
from typing import Callable, Optional
from jose import jwt
from starlette.requests import Request
from armasec import OpenidConfigLoader, TokenManager, TokenSecurity
from armasec.token_decoder import TokenDecoder
from armasec.exceptions import AuthenticationError
from armasec.token_payload import TokenPayload
from armasec.utilities import log_error
from armasec.schemas.armasec_config import DomainConfig
from armasec.token_security import ManagerConfig


class KeycloakTokenDecoder(TokenDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def decode(self, token: str, **claims) -> TokenPayload:
        """
        Decodes a jwt into a TokenPayload while checking signatures and claims.
        """
        self.debug_logger(f"Attempting to decode '{token}'")
        self.debug_logger(f"  checking claims: {claims}")
        with AuthenticationError.handle_errors(
            "Failed to decode token string",
            do_except=partial(log_error, self.debug_logger),
        ):
            payload_dict = dict(
                jwt.decode(
                    token,
                    self.get_decode_key(token),
                    algorithms=[self.algorithm],
                    options=self.decode_options_override,
                    **claims,
                )
            )

            # get permissions from keycloak token
            permissions = [
                scope
                for permission in payload_dict["authorization"]["permissions"]
                if "scopes" in permission
                for scope in permission["scopes"]
            ]

            payload_dict["permissions"] = permissions

            self.debug_logger(f"Payload dictionary is {payload_dict}")
            self.debug_logger("Attempting to convert to TokenPayload")
            token_payload = TokenPayload(**payload_dict)

            self.debug_logger(f"Built token_payload as {token_payload}")
            return token_payload


class KeycloakArmasec:
    # TODO: make this mirror the Armasec class and make sure that the lock shows up
    #       in the swagger docs.
    def __init__(
        self,
        openid_config: OpenidConfigLoader,
        audience: str,
        scopes: list[str] = None,
        debug_logger: Optional[Callable[..., None]] = None,
    ):
        self.openid_config = openid_config

        self.domain_config = DomainConfig(
            domain=openid_config.domain, audience=audience
        )

        self.token_decoder = KeycloakTokenDecoder(
            jwks=self.openid_config.jwks,
            debug_logger=debug_logger,
        )

        self.token_manager = TokenManager(
            openid_config=self.openid_config,
            token_decoder=self.token_decoder,
            audience=audience,
            debug_logger=debug_logger,
        )

        self.token_manager_config = ManagerConfig(
            manager=self.token_manager, domain_config=self.domain_config
        )

        self.armasec = TokenSecurity(
            domain_configs=[self.domain_config],
            scopes=scopes,
            debug_logger=debug_logger,
        )
        self.armasec.managers = [self.token_manager_config]

    async def __call__(self, request: Request) -> TokenPayload:
        return await self.armasec(request)
