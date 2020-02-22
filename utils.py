from db import get_db
from datetime import datetime, timedelta, date, time


# Deprecated
def remove_timeout_user(user_id, now, hour=12):
    c = get_db()
    res = c.execute(f'select wake_timestamp from rest_record where id ={user_id}').fetchone()  # res 为一个元组
    if res is None:
        return

    waken_time = datetime.fromtimestamp(res[0])
    now = datetime.fromtimestamp(now)
    duration = now - waken_time
    if duration > timedelta(hours=hour):
        c.execute(f'delete from rest_record where id ={user_id}')


def reply(msg, at_sender=True):
    now = datetime.now().timestamp()
    # 构造log所需的context
    log({'message': msg, 'sender': {'nickname': 'zaobot'}, 'time': now, 'user_id': 0})
    return {'reply': msg, 'at_sender': at_sender}


def log(context):
    c = get_db()
    time = datetime.fromtimestamp(context['time'])
    inserted_data = (context['message'], get_nickname(context),
                     context['user_id'], context['time'], str(time))
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
        if args[0].get('group_id') == 102334415 \
                and (args[0]['sender'].get('role') == 'owner' or args[0]['sender'].get('role') == 'admin'):
            return self.func(*args, **kwargs)
        else:
            return reply("你没有权限o(≧口≦)o")


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

    import requests
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
                          f'你已经成功突破了{xiuxian_level[level][0]}期，进入{xiuxian_level[level+1][0]}期。')
            level += 1
        c.execute('update xiuxian_emulator '
                  'set level=?, exp=?, last_speaking_timestamp=?, last_speaking_time=? where id=?',
                  (level, exp, now_datetime.timestamp(), now_datetime.isoformat(), user['id']))
        if get_nickname(context) != user['nickname']:
            c.execute('update xiuxian_emulator set nickname=? where id=?', (get_nickname(context), user['id']))
        c.commit()
