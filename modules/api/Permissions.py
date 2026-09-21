import functools
import json
from enum import IntEnum

from fastapi import status

from DNDBot import DNDBot


def permissions(permissions_value: 'Permissions'):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper_decorator(*args, **kwargs):
            token = kwargs.get("auth", "")
            permissions_level = check_authorization(token)
            print(token, permissions_level, permissions_value, permissions_level & permissions_value)
            if permissions_level & permissions_value == 0:
                response = kwargs.get("response", None)
                if response is not None:
                    response.status_code = status.HTTP_401_UNAUTHORIZED
                return json.dumps({"error": "Unauthorized"})
            return await func(*args, **kwargs)

        return wrapper_decorator
    return decorator


class Permissions(IntEnum):
    NONE = 0b0
    CAMPAIGN_READ = 0b1
    CAMPAIGN_WRITE = 0b10
    CAMPAIGN_CREATE = 0b100
    USER_READ = 0b1000
    USER_WRITE = 0b10000
    USER_CREATE = 0b100000
    FULL = 0b11111111


def check_authorization(auth: str) -> int:
    user = DNDBot.instance.db.execute("SELECT * FROM authorized_users WHERE token=?", (auth,)).fetchone()
    if user is not None:
        return user["permissions"]
    return 0
