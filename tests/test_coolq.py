import pytest
from datetime import datetime
import sqlite3
# from pprint import pprint
from bot.db import get_db


def data_generator(
        message,
        user_id: int = 1,
        time: datetime.isoformat = '2019-01-01 00:08:00',
        role: str = 'member',
        card: str = 'test_card',
        nickname: str = 'test_nickname',
        message_type: str = 'group'
):
    message = "/" + message
    timestamp = datetime.fromisoformat(time).timestamp()
    data = {
        "anonymous": "None",
        "font": 1591808,
        "group_id": 102334415,
        "message": message,
        "message_id": 1,
        "message_type": message_type,
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
    try:
        return response.json['reply']
    except TypeError:
        return


def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()

    # 退出环境后， 连接应当已关闭
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)


def test_invalid_request(client):
    r = client.post('/', json={"hello": "world"})
    assert r.status_code == 400


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
    response = client.post('/', json=data_generator('zao', time='2019-12-01 08:01:00', user_id=101, card='no1'))
    assert '第2起床' in response.json['reply']


def test_fake_wan(client):
    response = client.post('/', json=data_generator('wan', time='2019-12-01 08:20:00'))
    assert '你不是才起床吗' in response.json['reply']


def test_wan(client):
    response = client.post('/', json=data_generator('wan', time='2019-12-01 21:00:00'))
    assert '13小时00分00秒' in response.json['reply']


def test_wan_with_delay(client):
    send(client, 'zao', time='2019-12-01 08:01:00', user_id=102, card='no2')
    r = send(client, 'wan 1', time='2019-12-01 21:00:00', user_id=102, card='no2')
    print(r)
    assert '13小时00分00秒' in r


def test_wan_invalid(client):
    send(client, 'zao', time='2019-12-01 08:00:00', user_id=103, card='no3')
    r = send(client, 'wan joke', time='2019-12-01 21:00:00', user_id=103, card='no3')
    assert '13小时00分00秒' in r


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


def test_say(client):
    assert "你必须说点什么" in send(client, 'say')
    assert "我记在脑子里啦" in send(client, 'say anything')


def test_private_only_decorator(client):
    print(send(client, 'rest_statistic'))
    assert "请私聊我获取作息统计信息。" in send(client, 'rest_statistic')


def test_rest_statistic(client):
    response = send(client, 'rest_statistic', message_type='private')
    print(response)
    assert "平均" in response
    assert "暂无数据。" in send(client, 'rest_statistic', user_id=101, message_type='private')


def test_zao_second_day(client):
    assert '第1起床' in send(client, 'zao', time='2019-12-02 12:00:00')
    assert '第2起床' in send(client, 'zao', time='2019-12-02 12:00:00', user_id=101, card='no1')


def test_log(app):
    with app.app_context():
        c = get_db()
        log = c.execute('select * from log').fetchall()
        for i in log:
            print(tuple(i))
        assert len(log) > 0


class MessageHandler:
    def __init__(self):
        self.message = ''

    def handler(self, request, context):
        self.message = request.json()['message']
        return request.json()


# def test_xiuxian(client, requests_mock):
#     r = MessageHandler()
#     requests_mock.post('http://127.0.0.1:5700/send_msg', json=r.handler)
#
#     send(client, 'wan', time='2019-12-04 01:00:00')
#     assert '成功筑基' in r.message
#
#     send(client, 'anything', time='2019-12-04 04:00:00')
#     assert '突破了' in r.message
#     print(r.message)
#
#
# def test_xiuxian_ranking(client):
#     response = send(client, 'xiuxian_ranking')
#     print(response)
#     assert 'test_card' in response

def test_abbreviation_query(client, requests_mock):
    class Callback:
        def __init__(self):
            self.data = [
                    {
                        "name": "zsbd",
                        "trans": [
                            "字数补丁",
                            "这说不定",
                        ]
                    }
                ]
            self.status_code = 200

        def handler(self, request, context):
            context.status_code = self.status_code
            return self.data

    callback = Callback()
    requests_mock.post("https://lab.magiconch.com/api/nbnhhsh/guess", json=callback.handler)
    r = send(client, 'sxcx zsbd')
    print(r)
    assert "字数补丁" in r

    # test only one translation
    callback.data = [{"name": "zsbd", "trans": ["搞黄色"]}]
    assert "搞黄色" in send(client, 'sxcx ghs')

    # test if no translation
    callback.data = [{"name": "aaaa", "inputting": []}]
    assert "未找到aaaa的解释" in send(client, 'sxcx aaaa')

    # test if there are two words
    callback.data = [
      {
        "name": "aa",
        "trans": [
          "啊啊",
        ]
      },
      {
        "name": "aaa",
        "trans": [
          "啊啊啊",
        ]
      }
    ]
    r = send(client, 'sxcx aaaaa')
    assert "aa 可能是啊啊的缩写。" in r
    assert "aaa 可能是啊啊啊的缩写。" in r
    assert not r.endswith('\n')  # test end of line

    # test if upstream format changed
    callback.data = []
    assert "上游似乎出锅了" in send(client, 'sxcx zsbd')
    callback.data = [{"hahaa": "haha"}]
    assert "上游似乎出锅了" in send(client, 'sxcx zsbd')
