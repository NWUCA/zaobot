import pytest
# from coolq import handle_msg
from coolq import *
from datetime import datetime, time, date, timedelta
import sqlite3
import os
import json
from pprint import pprint
from db import get_db


# @pytest.fixture(scope="session")
# def data():
#     with open('test_data.json', 'r') as f:
#         yield json.load(f)
#
#
# def test_zao(c, data):  # handle_msg 中应该调用的是当前的 cursor
#     assert '第1起床' in handle_msg(data['zao'])['reply']
#
#
# def test_fake_wan(c, data):
#     assert '你不是才起床吗' in handle_msg(data['fake_wan'])['reply']
#
#
# def test_wan(c, data):
#     assert '13小时' in handle_msg(data['wan'])['reply']
#
# def test_log(c):
#     c.execute('select * from log')
#     log = c.fetchall()
#     pprint(log)
#     assert len(log) > 0

def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)

# def test_failure():
#     assert 0