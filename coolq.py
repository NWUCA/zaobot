from cqhttp import CQHttp
import re
from datetime import datetime, date, timedelta
import json
import random
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

bot = CQHttp(api_root='http://127.0.0.1:5700/')

today_date = date.today()
repeat_mode = 0

try:
    with open('waken_list.json', 'r') as f:
        waken_list = json.load(f)
    with open('waken_num.json', 'r') as f:
        waken_num = json.load(f)
except IOError:
    waken_num = 0
    waken_list = {}


def reply(msg, at_sender=True):
    return {'reply': msg, 'at_sender': at_sender}


def remove_timeout_user(user_id, now, hour=12):
    if waken_list.get(user_id) is None:
        return

    waken_time = datetime.fromtimestamp(waken_list[user_id]['time'])
    now = datetime.fromtimestamp(now)
    duration = now - waken_time
    if duration > timedelta(hours=hour):
        del waken_list[user_id]


@bot.on_message()
def handle_msg(context):
    global today_date, waken_num, repeat_mode
    if re.match('/', context['message']) is not None:
        message = context['message'][1:]
        message = message.split()
        command = message[0]
        args = message[1:]

        remove_timeout_user(context['user_id'], context['time'], 48)

        # 新的一天
        if date.fromtimestamp(context['time']) != today_date:
            today_date = date.fromtimestamp(context['time'])
            waken_num = 0

        if command == 'help':
            return {'reply': '我的源码存放在：github.com/cjc7373/zaobot，尽情探索吧。'}

        elif command == 'zao':
            remove_timeout_user(context['user_id'], context['time'])

            if waken_list.get(context['user_id']) is None:
                waken_list[context['user_id']] = {'time': context['time']}
                if context['sender'].get('card') is None:
                    waken_list[context['user_id']]['nickname'] = context['sender']['nickname']
                else:
                    waken_list[context['user_id']]['nickname'] = context['sender']['card']
                waken_num += 1
                # if waken_num == 1:
                #     bot.send(context, "获得成就：早起冠军")
                try:
                    greeting = args[0]
                except IndexError:
                    greeting = '少年'
                return {'reply': f"你是第{waken_num:d}起床的{greeting}。"}
            else:
                return {'reply': f"你不是起床过了吗？"}

        elif command == 'wan':
            if waken_list.get(context['user_id']) is None:
                return {'reply': 'Pia!<(=ｏ ‵-′)ノ☆ 不起床就睡，睡死你好了～'}
            sleep_time = datetime.fromtimestamp(context['time'])
            wake_time = datetime.fromtimestamp(waken_list[context['user_id']]['time'])
            duration = sleep_time - wake_time
            if duration < timedelta(minutes=30):
                return reply("你不是才起床吗？")
            else:
                del waken_list[context['user_id']]
                return {'reply': '今日共清醒{}秒，辛苦了'.format(
                    str(duration).replace(':', '小时', 1).replace(':', '分', 1)
                )}

        elif command == 'zaoguys':
            waken_list_sorted = sorted(waken_list.items(), key=lambda value: value[1]['time'])
            msg = ""
            index = 1
            for person in waken_list_sorted:
                waken_time = datetime.fromtimestamp(person[1]['time'])
                waken_date = date.fromtimestamp(person[1]['time'])
                if waken_date == today_date:
                    msg += f"\n{index}. {person[1]['nickname']}, {waken_time.hour:02d}:{waken_time.minute:02d}"
                    index += 1
            if msg == "":
                return {'reply': 'o<<(≧口≦)>>o 还没人起床'}
            return {'reply': msg}

        elif command == 'flush':
            return flush_handler(context)

        elif command == 'fudu':
            return fudu_handler(context)

        elif command == 'save':
            return save_handler(context)

        elif command == 'ask':
            try:
                question = args[0]
            except IndexError:
                return reply("说一个二元问题(´・ω・`)")
            if random.randrange(2) == 1:
                return reply("Yes")
            else:
                return reply("No")

        elif command == 'say':
            try:
                args[0]
            except:
                return reply("你必须说点什么。")

            secret = " ".join(args)
            r.lpush('secrets', secret)
            return reply("我记在脑子里啦！")

        # elif command == 'dig':
        #     total_length = r.llen('secrets')
        #     rand = random.randrange(total_length)
        #     secret = r.lrange('secrets', rand, rand)[0]
        #     return reply("某个人说：" + secret, False)

        else:
            pass
            # return {'reply': '听不懂<(=－︿－=)>'}

    elif repeat_mode:
        return {'reply': context['message'], 'at_sender': False}


class admin_required():
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        if args[0].get('group_id') == 102334415 \
                and (args[0]['sender'].get('role') == 'owner' or args[0]['sender'].get('role') == 'admin'):
            return self.func(*args, **kwargs)
        else:
            return reply("你没有权限o(≧口≦)o")


@admin_required
def fudu_handler(context):
    global repeat_mode
    if repeat_mode == 0:
        repeat_mode = 1
        return {'reply': "复读模式已开启(๑•̀ㅂ•́)و✧"}
    else:
        repeat_mode = 0
        return {'reply': "复读模式已关闭～(　TロT)σ"}


@admin_required
def save_handler(context):
    try:
        with open('waken_list.json', 'w') as f:
            json.dump(waken_list, f)
        with open('waken_num.json', 'w') as f:
            json.dump(waken_num, f)
        return reply("持久化数据成功。")
    except IOError as e:
        return reply(e)


@admin_required
def flush_handler(context):
    if context['user_id'] == 617175214:
        return reply("狗滑稽又来删库了(╯°Д°)╯︵ ┻━┻")
    global today_date, waken_num, repeat_mode
    waken_list.clear()
    waken_num = 0
    repeat_mode = 0
    today_date = date.today()
    return {'reply': "清除数据成功。"}


if __name__ == "__main__":
    bot.run(host='0.0.0.0', port=8080, debug=True)
