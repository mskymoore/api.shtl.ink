from functools import partial
from jose import jwt
from armasec.token_decoder import TokenDecoder
from armasec.exceptions import AuthenticationError
from armasec.token_payload import TokenPayload
from armasec.utilities import log_error


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
            self.debug_logger(f"Payload dictionary is {payload_dict}")
            self.debug_logger("Attempting to convert to TokenPayload")
            token_payload = TokenPayload(**payload_dict)

            # get permissions from keycloak token
            permissions = token_payload.authorization["permissions"][0]["scopes"]
            token_payload.permissions = permissions

            self.debug_logger(f"Built token_payload as {token_payload}")
            return token_payload
