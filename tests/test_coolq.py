from datetime import datetime
import sqlite3
from pprint import pprint
import re
import json

import pytest

from bot.db import get_db


def data_generator(
    message,
    user_id: int = 1,
    time: datetime.isoformat = '2019-01-01 00:08:00',
    role: str = 'member',
    card: str = 'test_card',
    nickname: str = 'test_nickname',
    message_type: str = 'group',
    auto_prefix_slash: bool = True
):
    if auto_prefix_slash:
        message = "/" + message
    assert message_type in ('group', 'private')
    timestamp = datetime.fromisoformat(time).timestamp()
    data = {
        "anonymous": "None",
        "font": 1591808,
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
    if message_type == 'group':
        data["group_id"] = 102334415
    return data


def send(client, *args, **kwargs):
    response = client.post('/', json=data_generator(*args, **kwargs))
    try:
        return response.json['reply']
    except TypeError:
        return


def test_data_generator():
    with pytest.raises(AssertionError):
        data_generator('help', message_type='fake')


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
    pprint(response.json)
    assert 'github' in response.json['reply']
    assert '/zao' in response.json['reply']


def test_zao(client):
    response = client.post('/', json=data_generator('zao', time='2019-12-01 08:00:00'))
    assert '第1起床' in response.json['reply']


def test_zao_db(app):
    with app.app_context():
        c = get_db()
        res = c.execute("select * from rest_record").fetchone()
        print(tuple(res))


def test_second_zao(client):
    response = client.post('/', json=data_generator('zao', time='2019-12-01 08:01:00',
                                                    user_id=101, card='no1'))
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
    assert '你没有权限' in send(client, 'flush', message_type='private')


def test_zaoguys(client):
    response = client.post('/', json=data_generator('zaoguys', time='2019-12-01 22:00:00'))
    print(response.json)


def test_say(client, app):
    assert "你必须说点什么" in send(client, 'say')
    assert "我记在脑子里啦" in send(client, 'say anything')
    with app.app_context():
        db = get_db()
        res = db.execute('select * from treehole').fetchall()
        assert len(res) != 0


def test_dig(client):
    assert "某个人说：" in send(client, 'dig')


def test_private_only_decorator(client):
    print(send(client, 'rest_statistic'))
    assert "请私聊我获取作息统计信息。" in send(client, 'rest_statistic')


def test_rest_statistic(client):
    response = send(client, 'rest_statistic', message_type='private')
    print(response)
    assert "暂无数据。" in response
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


def test_xiuxian(client, requests_mock):
    r = MessageHandler()
    requests_mock.post('http://127.0.0.1:5700/send_msg', json=r.handler)

    send(client, 'wan', time='2019-12-04 01:00:00')
    assert '成功筑基' in r.message

    send(client, 'anything', time='2019-12-04 04:00:00')
    assert '突破了' in r.message
    print(r.message)


def test_xiuxian_ranking(client):
    response = send(client, 'xiuxian_ranking')
    print(response)
    assert 'test_card' in response


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


class SimpleCallback:
    def __init__(self):
        self.data = {}

    def handler(self, request, context):
        self.data = request.json()
        return self.data


def test_ask(client, requests_mock):
    callback = SimpleCallback()
    requests_mock.register_uri('GET', "https://yesno.wtf/api/", real_http=True)
    requests_mock.post("/send_msg", json=callback.handler)
    send(client, 'ask anything')
    message = callback.data['message']
    assert message[0]['type'] == 'reply'
    assert "yes" in message[1]['data']['text'] or "no" in message[1]['data']['text']
    assert "说一个二元问题" in send(client, 'ask')


class TelegramBotApiCallback:
    def __init__(self):
        self.qs = {}
        self.rtn = {}

    def handler(self, request, context):
        self.qs = request.qs  # querystring
        res = {"message_id": -1, "date": "fake", "chat": None}
        if request.path.split('/')[-1] == 'sendmediagroup':
            res = [res]
        rtn = {"ok": True, "result": res}
        self.rtn = rtn
        return rtn


def test_cai(client, requests_mock, app):
    callback = TelegramBotApiCallback()

    # 必须匹配开头, 否则会在 bot api 的 querystring 中被匹配到
    matcher = re.compile('^https://www.baidu|^https://aip.baidu|^https://i.loli.net')

    requests_mock.register_uri('GET', matcher, real_http=True)
    requests_mock.register_uri('POST', matcher, real_http=True)

    requests_mock.post("/set_group_ban", json=callback.handler)
    requests_mock.post("/delete_msg", json=callback.handler)

    def send_msg_callback(request, context):
        # print(request.json())
        assert "违规内容" in request.json()['message']
        return {"data": "success"}

    requests_mock.post("/send_msg", json=send_msg_callback)

    send(client, "我好菜啊", user_id=595811044, auto_prefix_slash=False)
    assert callback.rtn != {}

    callback.rtn = {}
    send(client, "我好菜啊", user_id=595811044, auto_prefix_slash=False, message_type='private')
    assert callback.rtn == {}

    send(client, "我觉得还行", auto_prefix_slash=False)
    assert callback.rtn == {}

    send(client,
         "[CQ:image,file=75990CA9A3853BD3532E44B689D24675.png,"
         "url=https://www.baidu.com/img/bd_logo1.png]",
         user_id=595811044,
         auto_prefix_slash=False)
    assert callback.rtn == {}

    callback.rtn = {}
    send(client,
         "[CQ:image,file=75990CA9A3853BD3532E44B689D24675.png,"
         "url=https://i.loli.net/2020/05/11/Ft5OoR7p9TswHYk.png]",
         user_id=595811044,
         auto_prefix_slash=False)
    assert callback.rtn != {}

    callback.rtn = {}
    send(client,
         "哈哈哈哈 [CQ:image,file=75990CA9A3853BD3532E44B689D24675.png,"
         "url=https://i.loli.net/2020/05/11/Ft5OoR7p9TswHYk.png]",
         user_id=595811044,
         auto_prefix_slash=False)
    assert callback.rtn != {}


def test_send_to_tg(client, requests_mock, config, app):
    callback = TelegramBotApiCallback()
    requests_mock.post(
        app.config['TELEGRAM_API_ADDRESS'].format(app.config['TELEGRAM_API_TOKEN'], "sendMessage"),
        json=callback.handler
    )
    requests_mock.get(
        app.config['TELEGRAM_API_ADDRESS'].format(app.config['TELEGRAM_API_TOKEN'], "sendMediaGroup"),
        json=callback.handler
    )

    send(client, "我觉得还行", auto_prefix_slash=False)
    print(callback.qs)
    assert callback.qs['text'][0] == '[test_card(test_nickname)]: 我觉得还行'

    send(client,
         "[CQ:image,file=75990CA9A3853BD3532E44B689D24675.png,"
         "url=https://www.baidu.com/img/bd_logo1.png]",
         user_id=1195944745,
         auto_prefix_slash=False)
    print(callback.qs)
    res = json.loads(callback.qs['media'][0])
    assert res == \
           [{'type': 'photo', 'media': 'https://www.baidu.com/img/bd_logo1.png',
             'caption': '[test_card(test_nickname)]:  '}]


def test_randomly_save_message_to_treehole(app):
    # we don't use HTTP client because it's too slow
    from bot.utils import randomly_save_message_to_treehole
    from bot.context import GroupContext
    data = data_generator('foobar', auto_prefix_slash=False)
    context = GroupContext(data)

    with app.app_context():
        for _ in range(1000):
            randomly_save_message_to_treehole(context)

        db = get_db()
        res = db.execute('select * from treehole').fetchall()
        print("Len =", len(res))
        assert len(res) != 0


def test_webhook(client, requests_mock):
    data = {
        'commits': [
            {'id': '1234567', 'message': "test1"},
            {'id': '2345678', 'message': "test2"},
        ],
        'sender': {
            'login': 'user1'
        }
    }
    r = MessageHandler()
    requests_mock.post('http://127.0.0.1:5700/send_msg', json=r.handler)
    client.post('/webhook', json=data, headers={'X-GitHub-Event': 'push'})
    print(r.message)
    assert 'user1 has pushed 2 commit(s)' in r.message

    data = {
        "action": "opened",
        "pull_request": {
            "html_url": "fake_url",
            "title": "foo",
        },
        'sender': {
            'login': 'user1'
        }
    }
    client.post('/webhook', json=data, headers={'X-GitHub-Event': 'pull_request'})
    print(r.message)
    assert 'user1 has opened a pull request: foo.\nFor details see: fake_url' in r.message


def test_ky_1(client):
    assert "管理员还未设定考研时间" in send(client, 'ky')


def test_setky(client):
    assert "考研时间格式必须为yyyyMMdd" in send(client, 'setky', role='admin')
    assert "考研时间格式必须为yyyyMMdd" in send(client, 'setky 1231', role='admin')
    assert "设置成功" in send(client, 'setky 20201122', role='admin')
    # for updates
    assert "设置成功" in send(client, 'setky 20201222', role='admin')


def test_ky_2(client):
    assert "年度研究生考试还有" in send(client, 'ky')


def test_ghs(client, requests_mock):
    r = MessageHandler()
    requests_mock.post('http://127.0.0.1:5700/send_msg', json=r.handler)
    send(client, '开车了', auto_prefix_slash=False)
    assert 'gkd' in r.message


def test_scheduled_task(app, requests_mock):
    """
    所有定时任务都在这里测试.
    """
    from bot.scheduled_tasks import init_background_tasks

    r = MessageHandler()
    requests_mock.post('http://127.0.0.1:5700/send_msg', json=r.handler)

    with app.app_context():
        c = get_db()
        c.execute("update misc set value = '0' where key = 'mutex'")
        c.commit()

    scheduler = init_background_tasks(app)

    scheduler.get_job('ky_reminder').func()
    assert '年度研究生考试还有' in r.message

    scheduler.get_job('ghs_reminder').func()
    assert '距离上次 ghs 已经过去' in r.message


def test_q(client, requests_mock):
    class Callback:
        def __init__(self):
            self.data = {
                "message": "success",
                "data": {
                    "type": 5000,
                    "info": {
                        "text": "姚明的身高是226厘米"
                    }
                }
            }
            self.status_code = 200

        def handler(self, request, context):
            context.status_code = self.status_code
            return self.data

    callback = Callback()

    requests_mock.get("https://api.ownthink.com/bot?spoken=姚明多高啊？", json=callback.handler)
    r = send(client, 'q 姚明多高啊？')
    print(r)
    assert "姚明的身高是226厘米" in r


def test_json_extractor(client, requests_mock):
    text = r'[CQ:json,data={"config":{"type":"normal"&#44;"ctime":1610592580&#44;"forward":true&#44;"token' \
           r'":"a386f06d8f0621377feedcc0e7074a23"&#44;"autosize":true}&#44;"prompt":"&#91;分享&#93;【男子约见男网友睡醒钱被转走 ' \
           r'：“我对不起老婆孩子”…"&#44;"app":"com.tencent.structmsg"&#44;"ver":"0.0.0.1"&#44;"view":"news"&#44;"meta":{' \
           r'"news":{"action":""&#44;"source_url":""&#44;"android_pkg_name":""&#44;"jumpUrl":"https:\/\/m.okjike.com' \
           r'\/originalPosts\/5ffecea1454ac60018b53df1?s=ewoidSI6ICI1YWY4MzQzNmU4YzZiMTAwMTE5OTZhNzEiCn0%3D&amp' \
           r';utm_source=qq"&#44;"preview":"https:\/\/external-30160.picsz.qpic.cn\/65e1ea257c736c75507a80746ccd660b' \
           r'\/jpg1"&#44;"title":"【男子约见男网友睡醒钱被转走 ' \
           r'：“我对不起老婆孩子”…"&#44;"app_type":1&#44;"source_icon":""&#44;"tag":"即刻"&#44;"appid":1104252239&#44;"desc' \
           r'":"即刻App，身边最有意思的人都在玩了"}}&#44;"desc":"新闻"}] '
    text2 = r'[CQ:json,data={"app":"com.tencent.miniapp_01"&#44;"config":{' \
            r'"autoSize":0&#44;"ctime":1609952789&#44;"forward":1&#44;"height":0&#44;"token' \
            r'":"02ca89d519e7d1c6b39cad42ed6e0606"&#44;"type":"normal"&#44;"width":0}&#44;"desc' \
            r'":"知乎问答：你见过最大的扁桃体结石有多大？"&#44;"extra":{' \
            r'"app_type":1&#44;"appid":100490701&#44;"uin":646801992}&#44;"meta":{"detail_1":{' \
            r'"appid":"1110081493"&#44;"desc":"来自话题「扁桃体」，已有 171 个回答，305 人关注"&#44;"host":{"nick":"       ' \
            r'"&#44;"uin":646801992}&#44;"icon":"http://miniapp.gtimg.cn/public/appicon' \
            r'/0d7421ea21950d2b895d0c04c7ac2712_200.jpg"&#44;"preview":"https://pic3.zhimg.com/v2' \
            r'-40d33375a229b8bb9a32fddff1493b64.jpg"&#44;"qqdocurl":"http://www.zhihu.com/question/322903679' \
            r'?utm_source=qq&amp;utm_medium=social&amp;utm_oi=657656659866947584"&#44;"scene":1036&#44' \
            r';"shareTemplateData":{}&#44;"shareTemplateId":"8C8E89B49BE609866298ADDFF2DBABA4"&#44;"title' \
            r'":"知乎问答：你见过最大的扁桃体结石有多大？"&#44;"url":"m.q.qq.com/a/s/40c2d9c863258c04e12a8f727b2e089a"}}&#44' \
            r';"needShareCallBack":false&#44;"prompt":"&#91;QQ小程序&#93;知乎问答：你见过最大的扁桃体结石有多大？"&#44;"ver":"1.0.0.19"&#44' \
            r';"view":"view_8C8E89B49BE609866298ADDFF2DBABA4"}] '

    def send_msg_callback(request, context):
        # print(request.json())
        m = request.json()['message']
        assert "男子约见男网友睡醒钱被转走" in m or "你见过最大的扁桃体结石有多大" in m
        return {"data": "success"}

    requests_mock.post("/send_msg", json=send_msg_callback)

    send(client, text, auto_prefix_slash=False)
    send(client, text2, auto_prefix_slash=False)
