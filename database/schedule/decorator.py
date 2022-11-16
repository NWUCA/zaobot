from typing import Callable, Dict
import functools

class Register:
    def __init__(self) -> None:
        self.members: Dict[str, Callable] = {}
    def __call__(self, key: str) -> None:
        def wrapper(func: Callable):
            self.members[key] = func
        return wrapper
    def _empty(*args, **kwargs):
        pass
    def get(self, key:str) -> Callable:
        return self.members.get(key, Register._empty)

register = Register()
