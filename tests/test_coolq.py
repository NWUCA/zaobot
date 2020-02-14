import pytest
from datetime import datetime, date, timedelta
import sqlite3
import os
import json
from pprint import pprint
from db import get_db


def data_generator(
        message,
        user_id: int = 1,
        time: datetime.isoformat = '2019-01-01 00:08:00',
        role: str = 'member',
        card: str = 'test_card',
        nickname: str = 'test_nickname'
):
    message = "/" + message
    timestamp = datetime.fromisoformat(time).timestamp()
    data = {
        "anonymous": "None",
        "font": 1591808,
        "group_id": 102334415,
        "message": message,
        "message_id": 1,
        "message_type": "group",
        "post_type": "message",
        "raw_message": message,
        "self_id": 0,
        "sender": {
            "age": 0,
            "area": "",
            "card": card,
            "level": "活跃",
            "nickname": nickname,
            "role": role,
            "sex": "unknown",
            "title": "头衔",
            "user_id": user_id
        },
        "sub_type": "normal",
        "time": timestamp,
        "user_id": user_id
    }
    return data


def send(client, *args, **kwargs):
    response = client.post('/', json=data_generator(*args, **kwargs))
    return response.json['reply']


def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()

    # 退出环境后， 连接应当已关闭
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)


def test_help(client):
    response = client.post('/', json=data_generator('help'))
    print(response.json)
    assert 'github' in response.json['reply']


def test_zao(client):
    response = client.post('/', json=data_generator('zao', time='2019-12-01 08:00:00'))
    assert '第1起床' in response.json['reply']


def test_zao_db(app):
    with app.app_context():
        c = get_db()
        res = c.execute("select * from rest_record").fetchone()
        print(tuple(res))
        assert 1


def test_second_zao(client):
    response = client.post('/', json=data_generator('zao', time='2019-12-01 08:01:00', user_id=101, card='no2'))
    assert '第2起床' in response.json['reply']


def test_fake_wan(client):
    response = client.post('/', json=data_generator('wan', time='2019-12-01 08:20:00'))
    assert '你不是才起床吗' in response.json['reply']


def test_wan(client):
    response = client.post('/', json=data_generator('wan', time='2019-12-01 21:00:00'))
    assert '13小时' in response.json['reply']


def test_admin(client):
    response = client.post('/', json=data_generator('flush'))
    assert '你没有权限' in response.json['reply']


def test_zaoguys(client):
    response = client.post('/', json=data_generator('zaoguys', time='2019-12-01 22:00:00'))
    print(response.json)
    assert 1


def test_ask(client):
    r = send(client, 'ask anything')
    assert "Yes" in r or "No" in r
    assert "说一个二元问题" in send(client, 'ask')


def test_log(app):
    with app.app_context():
        c = get_db()
        log = c.execute('select * from log').fetchall()
        for i in log:
            print(tuple(i))
        assert len(log) > 0


def test_say(client):
    assert "你必须说点什么" in send(client, 'say')
    assert "我记在脑子里啦" in send(client, 'say anything')