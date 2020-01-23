import pytest
# from coolq import handle_msg
from coolq import *
from datetime import datetime, time, date, timedelta
import sqlite3
import os
import json


@pytest.fixture(scope="session")
# 为了代码简单起见起了这样一个函数名
def c():
    connection = sqlite3.connect('test.db')
    cursor = connection.cursor()
    init.init_database(cursor)
    yield cursor
    cursor.close()
    connection.close()
    os.remove('test.db')


@pytest.fixture(scope="session")
def data():
    with open('test_data.json', 'r') as f:
        yield json.load(f)


def test_zao(c, data):  # handle_msg 中应该调用的是当前的 cursor
    assert '第1起床' in handle_msg(data['zao'])['reply']


def test_fake_wan(c, data):
    pass


def test_wan(c, data):
    assert '13小时' in handle_msg(data['wan'])['reply']
