from .db import get_db
from datetime import datetime, timedelta, date
import requests
import base64
import time
import re
from flask import current_app


def reply(msg, at_sender=True):
    now = datetime.now().timestamp()
    # 构造log所需的context
    log({'message': msg, 'sender': {'nickname': 'zaobot'}, 'time': now, 'user_id': 0})
    return {'reply': msg, 'at_sender': at_sender}


def log(context):
    c = get_db()
    log_time = datetime.fromtimestamp(context['time'])
    inserted_data = (context['message'], get_nickname(context),
                     context['user_id'], context['time'], str(log_time))
    c.execute("insert into log values (?,?,?,?,?)", inserted_data)
    c.commit()


def get_nickname(context):
    if context['sender'].get('card') is None:
        return context['sender']['nickname']
    else:
        return context['sender']['card']


class admin_required:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        if args[0]['sender'].get('role') == 'owner' or args[0]['sender'].get('role') == 'admin':
            return self.func(*args, **kwargs)
        else:
            return reply("你没有权限o(≧口≦)o")


class private_message_only:
    """仅限私聊指令的装饰器"""

    def __init__(self, func):
        self.func = func

    def __call__(self, context, args):
        if context['message_type'] != 'private':
            if self.func.__doc__ is None:
                rtn = f"使用 /{self.func.__name__} 指令。"
            else:
                rtn = self.func.__doc__.strip()
            return reply(f"请私聊我{rtn}")
        else:
            return self.func(context, args)


def average_rest_time(valid_record: list, delta: int) -> str:
    now = datetime.now().timestamp()
    record = [i for i in valid_record
              if timedelta(seconds=now - i['sleep_timestamp']) < timedelta(days=delta)]
    length = len(record)
    if length == 0:
        return ""
    wake_timedelta = timedelta()
    sleep_timedelta = timedelta()
    rest_time = timedelta()
    for i in record:
        wake_time = datetime.fromtimestamp(i['wake_timestamp'])
        sleep_time = datetime.fromtimestamp(i['sleep_timestamp'])
        rest_time += timedelta(hours=24) - (sleep_time - wake_time)  # rest_time 在日期被替换之前计算

        wake_time = wake_time.replace(2020, 1, 1)
        if sleep_time.hour < 12:
            sleep_time = sleep_time.replace(2020, 1, 2)
        else:
            sleep_time = sleep_time.replace(2020, 1, 1)

        wake_timedelta += wake_time - datetime(2020, 1, 1)
        sleep_timedelta += sleep_time - datetime(2020, 1, 2)

    avg_wake_time = (datetime(2020, 1, 1) + wake_timedelta / length).time().isoformat()
    avg_sleep_time = (datetime(2020, 1, 2) + sleep_timedelta / length).time().isoformat()
    avg_rest_time = int((rest_time / length).total_seconds() / 60)  # 单位为分钟
    avg_rest_time = f"{avg_rest_time // 60}小时{avg_rest_time % 60}分钟"
    return f"近{delta}天的平均入睡时间为{avg_sleep_time}, 平均起床时间为{avg_wake_time}, 平均睡眠时长为{avg_rest_time}。\n"


class Error(Exception):
    def __init__(self, status_code, ret_code=None):
        self.status_code = status_code
        self.ret_code = ret_code


def send(context, message, **kwargs):
    context = context.copy()
    context['message'] = message
    context.update(kwargs)
    if 'message_type' not in context:
        if 'group_id' in context:
            context['message_type'] = 'group'
        elif 'discuss_id' in context:
            context['message_type'] = 'discuss'
        elif 'user_id' in context:
            context['message_type'] = 'private'

    log({'message': message, 'sender': {'nickname': 'zaobot'}, 'time': context['time'], 'user_id': 0})

    url = 'http://127.0.0.1:5700/send_msg'
    resp = requests.post(url, json=context)
    if resp.ok:
        data = resp.json()
        if data.get('status') == 'failed':
            raise Error(resp.status_code, data.get('retcode'))
        return data.get('data')
    raise Error(resp.status_code)


xiuxian_level = (('筑基', 100),
                 ('开光', 300),
                 ('融合', 600),
                 ('心动', 1000),
                 ('金丹', 1500),
                 ('元婴', 2100),
                 ('出窍', 2800),
                 ('分神', 3600),
                 ('合体', 4500),
                 ('洞虚', 5500),
                 ('大乘', 6600),
                 ('渡劫', 7800))


def start_xiuxian(context):
    c = get_db()
    if not 0 <= datetime.fromtimestamp(context['time']).time().hour < 5:
        return
    if c.execute(f'select * from xiuxian_emulator where id = {context["user_id"]}').fetchone() is None:
        c.execute('insert into xiuxian_emulator values (?,?,?,?,?,?)',
                  (context['user_id'], get_nickname(context), 0, 0, '', ''))
        c.commit()
        send(context, f'@{get_nickname(context)}，你已经成功筑基，一个新的世界已经对你敞开！')
        accumulate_exp(context)


def accumulate_exp(context):
    c = get_db()
    now_datetime = datetime.fromtimestamp(context['time'])
    now_time = now_datetime.time()
    if not 0 <= now_time.hour < 8:
        return
    user = c.execute(f'select * from xiuxian_emulator where id = {context["user_id"]}').fetchone()
    if user is not None:
        if user['last_speaking_timestamp'] == "" \
                or date.fromtimestamp(user['last_speaking_timestamp']) != date.fromtimestamp(context['time']):
            last_speaking_datetime = now_datetime.replace(hour=0, minute=0, second=0)
        else:
            last_speaking_datetime = datetime.fromtimestamp(user['last_speaking_timestamp'])

        delta = now_datetime - last_speaking_datetime
        if now_time.hour < 5 or (timedelta(minutes=1) <= delta < timedelta(hours=3)):
            elapsed_minute = int(delta.total_seconds() / 60)
        else:
            return
        exp = user['exp'] + elapsed_minute
        level = user['level']
        while exp > xiuxian_level[level][1]:
            send(context, f'@{get_nickname(context)}，'
                          f'你已经成功突破了{xiuxian_level[level][0]}期，进入{xiuxian_level[level + 1][0]}期。')
            level += 1
        c.execute('update xiuxian_emulator '
                  'set level=?, exp=?, last_speaking_timestamp=?, last_speaking_time=? where id=?',
                  (level, exp, now_datetime.timestamp(), now_datetime.isoformat(), user['id']))
        if get_nickname(context) != user['nickname']:
            c.execute('update xiuxian_emulator set nickname=? where id=?', (get_nickname(context), user['id']))
        c.commit()


def update_baidu_ai_auth():
    """
    Baidu AI platform is used for ocr
    Auth doc: https://ai.baidu.com/ai-doc/REFERENCE/Ck3dwjhhu
    """
    host = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id" \
           "=z3B1bM2CjI3fi32zKj9toNIj&client_secret=RU5xGbR0uizZA2StvqWBGaGyEhDkF4b2"
    resp = requests.get(host)
    auth_token = {
        'access_token': resp.json()['access_token'],
        'created_time': time.time(),
        "expires_in": resp.json()['expires_in']
    }
    current_app.config['baidu_ai_auth'] = auth_token
    return auth_token


def ocr(base64_image):
    """
    Baidu OCR service
    DOC: https://ai.baidu.com/ai-doc/OCR/zk3h7xz52
    """
    baidu_ai_auth = current_app.config.get("baidu_ai_auth")
    if (baidu_ai_auth is None) or \
            (time.time() - baidu_ai_auth['created_time'] > baidu_ai_auth['expires_in'] - 86400):
        baidu_ai_auth = update_baidu_ai_auth()
    params = {"image": base64_image}
    request_url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?" \
                  f"access_token={baidu_ai_auth['access_token']}"
    response = requests.post(request_url, data=params,
                             headers={'content-type': 'application/x-www-form-urlencoded'})
    return " ".join(map(lambda a: a['words'], response.json()["words_result"]))


def find_cai(context):
    # 只针对环卫工有效
    if context['user_id'] != 595811044:
        return

    # Get image url
    msg = context["message"]
    images = re.findall(r"\[CQ:image,file=(.*?),url=(.*?)\]", msg)

    ocr_result = []
    for image in images:
        image_name = image[0]
        image_url = image[1]
        if image_name.endswith('gif'):
            continue
        content = requests.get(image_url).content
        ocr_result.append(ocr(base64.b64encode(content)))

    text = " ".join([context["message"]] + ocr_result)

    # re match
    cai_re = re.compile(r"[你|我|群]\s*?(.*){1}\s*?菜")
    if cai_re.search(text):
        post_data = {"group_id": context["group_id"], "user_id": context["user_id"], "duration": 60 * 20}
        requests.post("http://localhost:5700/set_group_ban", json=post_data)

        # delete message is only available in Coolq Pro
        # post_data = {"message_id": context["message_id"]}
        # requests.post("http://localhost:5700/delete_msg", json=post_data)

        # substitute [CQ:...] to image url
        def sub(matched):
            # print(matched[1], matched[2])
            return matched[2] + ' '

        processed_msg = re.sub(r"\[CQ:image,file=(.*?),url=(.*?)\]", sub, msg)
        send(context, f"违规内容：{get_nickname(context)} {datetime.fromtimestamp(context['time'])} {processed_msg}")


# Telegram bot API doc: https://core.telegram.org/bots/api
TELEGRAM_API_ADDRESS = "https://telegram.coherence.codes"
TELEGRAM_API_TOKEN = "bot793455209:AAEXy1I4cpaaN5m_C9YNrT5qoRN3He3ULxk"
TELEGRAM_CHAT_ID = "-387073882"  # A telegram group


# TODO 考虑非200 和超时等 exception
def tg_send_msg(text, chat_id=TELEGRAM_CHAT_ID):
    try:
        requests.post(f"{TELEGRAM_API_ADDRESS}/{TELEGRAM_API_TOKEN}/sendMessage",
                      json={"chat_id": chat_id, "text": text}, timeout=5)
    except requests.exceptions:
        pass


def tg_send_media_group(text, photo_urls, chat_id=TELEGRAM_CHAT_ID):
    """
    DOC: https://core.telegram.org/bots/api#sendmediagroup
    文档上写 media 必须是2-10个元素的 array，实际一个元素也可
    """
    media = [{"type": "photo", "media": url} for url in photo_urls]
    media[0]["caption"] = text  # 插入消息内容
    try:
        requests.post(f"{TELEGRAM_API_ADDRESS}/{TELEGRAM_API_TOKEN}/sendMediaGroup",
                      json={"chat_id": chat_id, "media": media},
                      timeout=5)
    except requests.exceptions:
        pass


def send_to_tg(context):
    name = get_nickname(context)
    msg_prefix = f"[{name}]:"
    image_re = re.compile(r"\[CQ:image,file=(.*?),url=(.*?)\]")
    image_urls = list(map(lambda a: a[1], re.findall(image_re, context['message'])))
    msg = re.sub(image_re, lambda a: " ", context['message'])
    if image_urls:
        tg_send_media_group(f"{msg_prefix} {msg}", image_urls)
    else:
        tg_send_msg(f"{msg_prefix} {msg}")
