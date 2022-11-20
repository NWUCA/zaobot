from typing import Dict
from random import random
class FuduCache:
    def __init__(self, message: str) -> None:
        self.count    = 1
        self.message  = message
        self.has_fudu = False
    def reset(self, message: str) -> None:
        self.__init__(message)
    def fudu(self):
        self.count = self.count + 1

all_cache : Dict[str, FuduCache] = {}

def should_fudu(group_id: str, message: str) -> bool:
    global all_cache
    if (cache := all_cache.get(group_id)) is None:
        all_cache[group_id] = FuduCache(message)
        return False
    if cache.message != message:
        cache.reset(message)
        return False
    cache.fudu()
    if cache.has_fudu:
        return False
    cache.has_fudu = random() < get_rate_of_fudu(cache.count)
    return cache.has_fudu

def get_rate_of_fudu(count: int) -> float:
    if count < 2:
        return 0.0
    if count >= 10:
        return 1.0
    return 1 / (10 - count)

