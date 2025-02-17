import datetime

import jwt

secret_key = 'PrEBxCvi8CkF6pWmHpzL'


class ReadTokenException(Exception):
    pass


def create_token(payload: dict) -> str:
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    return jwt.encode(payload, secret_key, algorithm='HS256')


def read_token(token: str) -> dict:
    try:
        return jwt.decode(token, secret_key, algorithms='HS256')
    except jwt.exceptions.PyJWTError:
        raise ReadTokenException
