import pytest
from datetime import datetime, time, date, timedelta
import sqlite3
import os
import json
from pprint import pprint
from db import get_db


def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()

    # 退出环境后， 连接应当已关闭
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)


def test_help(client, data):
    response = client.post('/', json=data['help'])
    print(response.json)
    assert 'github' in response.json['reply']


def test_zao(client, data):
    response = client.post('/', json=data['zao'])
    assert '第1起床' in response.json['reply']


def test_second_zao(client):
    data = {
        "message": "/zao",
        "sender": {
            "nickname": "user"
        },
        "post_type": "message",
        "time": 1575159400,
        "time_comment": "2019.12.1 8:16:40",
        "user_id": 101
    }
    response = client.post('/', json=data)
    assert '第2起床' in response.json['reply']

def test_fake_wan(client, data):
    response = client.post('/', json=data['fake_wan'])
    assert '你不是才起床吗' in response.json['reply']


def test_wan(client, data):
    response = client.post('/', json=data['wan'])
    assert '13小时' in response.json['reply']


def test_log(app):
    with app.app_context():
        c = get_db()
        log = c.execute('select * from log').fetchall()
        pprint(log)
        assert len(log) > 0
