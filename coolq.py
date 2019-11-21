from aiocqhttp import CQHttp
import re
from datetime import datetime, time, date, timedelta
import json

bot = CQHttp(enable_http_post=False)

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


def reply(msg):
    return {'reply': msg}

@bot.on_message()
async def handle_msg(context):
    global today_date
    global waken_num
    global repeat_mode
    if re.match('/', context['message']) is not None:
        message = context['message'][1:]
        message = message.split()
        command = message[1]
        args = message[1:]

        # 新的一天
        if date.fromtimestamp(context['time']) != today_date:
            today_date = date.fromtimestamp(context['time'])
            waken_num = 0

        if command == 'help':
            return {'reply': '我的源码存放在：github.com/cjc7373/zaobot，尽情探索吧。'}

        elif command == 'zao':
            if waken_list.get(context['user_id']):
                now = datetime.now()
                waken_time = datetime.fromtimestamp(waken_list[context['user_id']]['time'])
                duration = now - waken_time
                if duration > timedelta(hours=12):
                    del waken_list[context['user_id']]
            if waken_list.get(context['user_id']) is None:
                waken_list[context['user_id']] = {'time': context['time']}
                if context['sender'].get('card') is None:
                    waken_list[context['user_id']]['nickname'] = context['sender']['nickname']
                else:
                    waken_list[context['user_id']]['nickname'] = context['sender']['card']
                waken_num += 1
                if waken_num == 1:
                    await bot.send(context, "获得成就：早起冠军")
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
            del waken_list[context['user_id']]
            duration = sleep_time - wake_time
            if duration < timedelta(minutes=30):
                return reply(f"你不是才睡觉吗？")
            else:
                return {'reply': '今日共清醒{}秒，辛苦了'.format(
                    str(duration).replace(':', '小时', 1).replace(':', '分', 1)
                )}

        elif command == 'zaoguys':
            waken_list_sorted = sorted(waken_list.items(), key=lambda value: value[1]['time'])
            now = datetime.now()
            msg = ""
            index = 1
            for person in waken_list_sorted:
                waken_time = datetime.fromtimestamp(person[1]['time'])
                waken_date = date.fromtimestamp(person[1]['time'])
                duration = now - waken_time
                if duration > timedelta(hours=12):
                    del waken_list[person[0]]
                if waken_date == today_date:
                    msg += f"\n{index}. {person[1]['nickname']}, {waken_time.hour:02d}:{waken_time.minute:02d}"
                    index += 1
            if msg == "":
                return {'reply': 'o<<(≧口≦)>>o 还没人起床'}
            return {'reply': msg}

        elif command == 'flush':
            if context['sender'].get('role') == 'owner' or context['sender'].get('role') == 'admin'\
                    and context.get('group_id') == 102334415:
                waken_list.clear()
                waken_num = 0
                repeat_mode = 0
                today_date = date.today()
                return {'reply': "咱也不知道发生了什么，咱也不敢问。"}
            else:
                return {'reply': "你没有权限o(≧口≦)o"}

        elif command == 'fudu' \
                and context.get('group_id') == 102334415 \
                and (context['sender'].get('role') == 'owner' or context['sender'].get('role') ==  'admin'):
            if repeat_mode == 0:
                repeat_mode = 1
                return {'reply': "复读模式已开启(๑•̀ㅂ•́)و✧"}
            else:
                repeat_mode = 0
                return {'reply': "复读模式已关闭～(　TロT)σ"}

        elif command == 'save' \
                and context.get('group_id') == 102334415 \
                and (context['sender'].get('role') == 'owner' or context['sender'].get('role') == 'admin'):
            try:
                with open('waken_list.json', 'w') as f:
                    json.dump(waken_list, f)
                with open('waken_num.json', 'w') as f:
                    json.dump(waken_num, f)
                return reply("持久化数据成功。")
            except IOError as e:
                return reply(e)
        else:
            return {'reply': '听不懂<(=－︿－=)>'}

    elif repeat_mode:
        return {'reply': context['message'], 'at_sender': False}

bot.run(host='0.0.0.0', port=8080)
