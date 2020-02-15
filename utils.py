from db import get_db
from datetime import datetime, timedelta


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
        rest_time += timedelta(hours=24) - (sleep_time - wake_time) # rest_time 在日期被替换之前计算

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
