import datetime
import json
import math
import os

import requests
import settings


def cached_token(jsonfile):
    def has_valid_token(data):
        exp = math.ceil(
            (
                datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1, 0, 0, 0)
            ).total_seconds()
        )
        return "token" in data and exp < data["exp"]

    def get_token_from_file():
        with open(jsonfile) as f:
            data = json.load(f)
            if has_valid_token(data):
                return data.get("token")

    def save_token_to_file(token):
        with open(jsonfile, "w") as f:
            exp = math.ceil(
                (
                    datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1, 0, 0, 0)
                ).total_seconds()
            )
            json.dump({"token": token, "exp": exp + 3600}, f)

    def decorator(fn):
        def wrapped(*args, **kwargs):
            if os.path.exists(jsonfile):
                token = get_token_from_file()
                if token:
                    return token
            res = fn(*args, **kwargs)
            save_token_to_file(res)
            return res

        return wrapped

    return decorator


@cached_token(settings.TOKEN_FILE)
def get_jwt():
    form_data = {"username": settings.TOKEN_LOGIN, "password": settings.TOKEN_PASSWORD}
    r = requests.post(settings.TOKEN_URL, data=form_data)
    r.raise_for_status()
    token = r.json()

    return token.get('success')
