from typing import Callable, Dict

class TaskRegister:

    def __init__(self) -> None:
        self.members: Dict[str, Callable] = {}

    def __call__(self, key: str) -> None:
        def wrapper(func: Callable):
            self.members[key] = func
        return wrapper

    @staticmethod
    def _empty(*args, **kwargs):
        print('Warning: 正在使用失效的任务')

    def get(self, key: str) -> Callable:
        return self.members.get(key, TaskRegister._empty)

task_register = TaskRegister()
