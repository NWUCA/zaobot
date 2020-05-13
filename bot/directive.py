"""
zaobot的所有指令
"""

import random
# from flask import g, current_app
from datetime import date, datetime, timedelta
from .db import get_db
from .utils import reply, get_nickname, admin_required, average_rest_time, send
from .utils import xiuxian_level

import requests


# from .utils import *


def help(context, args):
    return reply('我的源码存放在：github.com/NWUCA/zaobot，尽情探索吧。')


def zao(context, args):
    c = get_db()

    today = date.fromtimestamp(context['time'])

    current_user = c.execute('select * from rest_record where id = ? and wake_time like ?',
                             (context["user_id"], str(today) + "%")).fetchone()
    if current_user is None or date.fromtimestamp(current_user['wake_timestamp']) != today:
        last_user = c.execute(
            "SELECT wake_timestamp, waken_num FROM rest_record ORDER BY wake_timestamp DESC LIMIT 1").fetchone()
        if last_user is None or date.fromtimestamp(last_user['wake_timestamp']) != today:
            # 新的一天
            waken_num = 1
        else:
            waken_num = last_user['waken_num'] + 1
        wake_timestamp = context['time']
        wake_time = datetime.fromtimestamp(context['time'])
        inserted_data = (
            context['user_id'], wake_timestamp, wake_time, get_nickname(context), waken_num, '', '')  # 注意顺序
        c.execute("insert into rest_record values (?,?,?,?,?,?,?)", inserted_data)
        c.commit()
        try:
            greeting = args[0]
        except IndexError:
            greeting = '少年'
        return reply(f"你是第{waken_num:d}起床的{greeting}。")
    elif current_user['sleep_timestamp'] != '':
        return reply("你不是睡了吗？")
    else:
        return reply("你不是起床过了吗？")


def wan(context, args):
    c = get_db()
    # start_xiuxian(context)
    current_user = c.execute(f'select wake_timestamp from rest_record '
                             f'where id ={context["user_id"]} ORDER BY wake_timestamp DESC LIMIT 1').fetchone()
    current_time = datetime.fromtimestamp(context['time'])
    if current_user is None \
            or current_time - datetime.fromtimestamp(current_user['wake_timestamp']) > timedelta(hours=24):
        return reply('Pia!<(=ｏ ‵-′)ノ☆ 不起床就睡，睡死你好了～')

    wake_time = datetime.fromtimestamp(current_user['wake_timestamp'])
    duration = current_time - wake_time
    if duration < timedelta(minutes=30):
        return reply("你不是才起床吗？")
    else:
        msg = ""
        try:
            delay_minute = int(args[0])
            sleep_time = current_time + timedelta(minutes=delay_minute)
            duration += timedelta(minutes=delay_minute)
            msg += f"将在{delay_minute}分钟后睡觉。\n"
        except (IndexError, ValueError):
            sleep_time = current_time

        c.execute(
            "update rest_record set sleep_timestamp = ?, sleep_time = ? "
            "where id = ? and wake_timestamp = ?",
            (sleep_time.timestamp(), sleep_time, context['user_id'], current_user['wake_timestamp']))
        c.commit()
        msg += '今日共清醒{}秒，辛苦了'.format(str(duration).replace(':', '小时', 1).replace(':', '分', 1))
        return reply(msg)


def zaoguys(context, args):
    c = get_db()
    today = date.fromtimestamp(context['time'])
    zao_list = c.execute(
        'select nickname, wake_timestamp from rest_record where wake_time like ?', (str(today) + "%",)).fetchall()
    msg = ""
    index = 1
    for person in zao_list:
        waken_time = datetime.fromtimestamp(person['wake_timestamp'])
        msg += f"\n{index}. {person['nickname']}, {waken_time.hour:02d}:{waken_time.minute:02d}"
        index += 1
    if msg == "":
        return reply('o<<(≧口≦)>>o 还没人起床')
    return reply(msg)


def ask(context, args):
    try:
        _ = args[0]
    except IndexError:
        return reply("说一个二元问题(´・ω・`)")
    if random.randrange(2) == 1:
        return reply("Yes")
    else:
        return reply("No")


def say(context, args):
    c = get_db()

    try:
        args[0]
    except IndexError:
        return reply("你必须说点什么。")

    secret = " ".join(args)
    timestamp = context['time']
    time = datetime.fromtimestamp(timestamp)
    c.execute("insert into treehole values (?,?,?,?,?)",
              (secret, timestamp, time, get_nickname(context), context['user_id']))
    c.commit()
    return reply("我记在脑子里啦！")


def backdoor(context, args):
    c = get_db()
    msg = ""
    try:
        timestamp = context['message'].replace("/backdoor ", "")
        res = c.execute(f"select * from treehole where timestamp = {timestamp}").fetchall()
        for i in res:
            msg += str(tuple(i)) + '\n'
    except IndexError:
        pass
    except Exception as e:
        msg = str(e)
    return reply(msg)


def dig():
    # total_length = r.llen('secrets')
    # rand = random.randrange(total_length)
    # secret = r.lrange('secrets', rand, rand)[0]
    # return reply("某个人说：" + secret, False)
    return reply("")


@admin_required
def flush(context, args):
    # c = get_db()
    # c.execute("delete from rest_record")
    return reply("清除数据成功。")


def rest_statistic(context, args):
    if context['message_type'] != 'private':
        return reply("请私聊我获得作息统计。")

    c = get_db()
    rest_list = c.execute('select * from rest_record where id = ?', (context["user_id"],)).fetchall()
    valid_record = [i for i in rest_list if i['sleep_time'] != '']
    msg = average_rest_time(valid_record, 7) + \
        average_rest_time(valid_record, 30) + \
        average_rest_time(valid_record, 365)
    if msg == "":
        return reply("暂无数据。")
    else:
        return reply(msg)


def xiuxian_ranking(context, args):
    c = get_db()
    res = c.execute('select * from xiuxian_emulator order by exp desc limit 10').fetchall()
    if len(res) == 0:
        return reply('呜呼！仙道中落，世间竟无人修仙！')
    msg = ""
    for i, person in enumerate(res):
        msg += f"{i + 1}. {person['nickname']} {xiuxian_level[person['level']][0]}期 " \
               f"经验{person['exp']}/{xiuxian_level[person['level']][1]}\n"
    return reply(msg, at_sender=False)


def send_test(context, args):
    send(context, 'test')


def sscx(context, args):
    """
    缩写查询，函数名为拼音缩写
    """
    word = args[0]
    data = {"text": word}
    r = requests.post('https://lab.magiconch.com/api/nbnhhsh/guess', json=data)
    try:
        r.json()[0]['name']
    except (IndexError, KeyError):
        return reply("上游似乎出锅了QAQ")
    resp_data = r.json()[0]
    trans = resp_data.get('trans')
    if trans is None:
        return reply("未找到相关的缩写。")
    return reply(f"{word} 可能是{','.join(trans)}的缩写。")
