import abc
import time
from numbers import Rational


class Context(abc.ABC):
    def __init__(self, payload):
        self.message = payload['message'].strip()
        self.message_id = payload['message_id']
        if self.message[0] == '/':
            message = self.message[1:].split()
            # May have Attribute Error, cause Context doesn't always have these attributes
            self.directive = message[0]
            self.args = message[1:]
        self.user_id = payload['user_id']
        self.time = payload['time']
        self.nickname = payload['sender'].get('nickname')
        self.message_type = None

    @classmethod
    def build(cls, message, time_: Rational = None, user_id=None, nickname=None):
        """Secondary construct method, construct a context from messages sent by zaobot"""
        return cls({
            'message': message,
            'message_id': -1,
            'time': time_ if time_ is not None else time.time(),
            'user_id': user_id if user_id is not None else 0,
            'sender': {
                'nickname': nickname if nickname is not None else 'zaobot'
            }
        })

    @property
    def name(self):
        if hasattr(self, 'group_card') and self.group_card != '':
            return self.group_card
        else:
            return self.nickname


class PrivateContext(Context):
    def __init__(self, payload):
        super().__init__(payload)
        self.message_type = "private"


class GroupContext(Context):
    def __init__(self, payload):
        super().__init__(payload)
        self.message_type = "group"
        self.group_id = payload['group_id']
        self.group_card = payload['sender'].get('card')  # could be empty string
        self.role = payload['sender'].get('role')
