#!.venv/bin/python3
import os
from requests import get
from dotenv import load_dotenv
from shtl_ink.shtl_ink_api.token import get_token

load_dotenv()

if __name__ == "__main__":

    username = (os.environ.get("TEST_USER"),)
    password = (os.environ.get("TEST_PASS"),)
    token = get_token(username, password)

    if token:
        for i in range(10):
            response = get(
                "http://localhost:8000/all_short_codes",
                headers={"Authorization": f"Bearer {token}"},
            )
            print(response.json())
