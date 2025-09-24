import os
import json

from shared.lib.error.errorKey import ErrorKey

LANG = "ja"

class BaseError(Exception):
    def __init__(self, key: ErrorKey, code = None, message = None):
        error = get_error(key)

        if code is None: self.code = code
        else: self.code = self.code = f"{error["category"]}-{error["code"]}"

        if message is None: self.message = message
        else: self.message = f"[{message}]"

        super().__init__(f"[{self.code}] {self.message}")

def get_error(key: ErrorKey):
    with open("./shared/lib/error/ErrorCode.json", "r") as f:
        ERRORS = json.load(f)

    return ERRORS[key]

def errorWrapper(key: ErrorKey, service_prefix = os.getenv("ERROR_PREFIX", "")):
    def decorator(func):
        def wrapper(*args, **kwargs):
            error = get_error(key)

            code = f"{error["category"]}-{error["code"]}"
            message = error["message"][LANG]

            try:
                result = func(*args, **kwargs)
                return True, result, None
            except BaseError as e:
                print(e, flush=True)
                return (
                    False,
                    None,
                    e
                )
            except Exception as e:
                print("ERROR", flush=True)
                print(e, flush=True)
                return  (
                    False,
                    None,
                    BaseError(
                        key,
                        code if service_prefix == "" else f"{service_prefix}-{code}",
                        f"({message})\n{e}"
                    )
                )
            
        return wrapper
    return decorator

def streamErrorWrapper(key: ErrorKey, service_prefix = os.getenv("ERROR_PREFIX", "")):
    def decorator(func):
        def wrapper(*args, **kwargs):
            error = get_error(key)

            code = f"{error["category"]}-{error["code"]}"
            message = error["message"][LANG]

            try:
                for res in func(*args, **kwargs):
                    yield True, res, None
            except BaseError as e:
                return (
                    False,
                    None,
                    e
                )
            except Exception as e:
                print(e, flush=True)
                return  (
                    False,
                    None,
                    BaseError(
                        key,
                        code if service_prefix == "" else f"{service_prefix}-{code}",
                        f"({message})\n{e}"
                    )
                )
            
        return wrapper
    return decorator

