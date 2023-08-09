from functools import partial
from typing import Callable, List, Optional
from jose import jwt
from starlette.requests import Request
from fastapi import HTTPException, status
from armasec import OpenidConfigLoader, TokenManager, TokenSecurity
from armasec.token_decoder import TokenDecoder
from armasec.exceptions import AuthenticationError
from armasec.token_payload import TokenPayload
from armasec.utilities import log_error
from armasec.schemas.armasec_config import DomainConfig
from armasec.token_security import ManagerConfig, PermissionMode


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
    def __init__(
        self,
        domain_configs: Optional[List[DomainConfig]] = None,
        debug_logger: Optional[Callable[..., None]] = None,
        debug_exceptions: bool = False,
        **kwargs,
    ):
        primary_domain_config = DomainConfig(**kwargs)
        if primary_domain_config.domain:
            self.domain_configs = [primary_domain_config]
        elif domain_configs is not None:
            self.domain_configs = domain_configs
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No domain was input.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        self.debug_logger = debug_logger
        self.debug_exceptions = debug_exceptions

        self.openid_configs = [
            OpenidConfigLoader(domain=domain_config.domain, use_https=True)
            for domain_config in self.domain_configs
        ]

        self.token_decoders = [
            KeycloakTokenDecoder(
                jwks=openid_config.jwks,
                debug_logger=debug_logger,
            )
            for openid_config in self.openid_configs
        ]

        self.token_managers = [
            TokenManager(
                openid_config=openid_config,
                token_decoder=token_decoder,
                audience=domain_config.audience,
                debug_logger=debug_logger,
            )
            for openid_config, token_decoder, domain_config in zip(
                self.openid_configs, self.token_decoders, self.domain_configs
            )
        ]

        self.token_manager_configs = [
            ManagerConfig(manager=token_manager, domain_config=primary_domain_config)
            for token_manager in self.token_managers
        ]

    def lockdown(
        self, *scopes: str, permission_mode: PermissionMode = PermissionMode.ALL
    ) -> TokenSecurity:
        lockdown_security = TokenSecurity(
            domain_configs=self.domain_configs,
            scopes=scopes,
            permission_mode=permission_mode,
            debug_logger=self.debug_logger,
            debug_exceptions=self.debug_exceptions,
        )
        lockdown_security.managers = self.token_manager_configs
        return lockdown_security

    def lockdown_all(self, *scopes: str) -> TokenSecurity:
        return self.lockdown(*scopes, permission_mode=PermissionMode.ALL)

    def lockdown_some(self, *scopes: str) -> TokenSecurity:
        return self.lockdown(*scopes, permission_mode=PermissionMode.SOME)
