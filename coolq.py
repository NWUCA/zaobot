from aiocqhttp import CQHttp
import re
from datetime import datetime, time, date, timedelta

bot = CQHttp(enable_http_post=False)

waken_list = {}
today_date = date.today()
waken_num = 0
repeat_mode = 0

@bot.on_message()
async def handle_msg(context):
    global today_date
    global waken_num
    global repeat_mode
    if re.match('/', context['message']) is not None:
        message = context['message'][1:]

        # 新的一天
        if date.fromtimestamp(context['time']) != today_date:
            today_date = date.fromtimestamp(context['time'])
            waken_num = 0

        if message == 'help':
            return {'reply': '我的源码存放在：github.com/cjc7373/zaobot，尽情探索吧。'}

        elif message == 'zao':
            if waken_list.get(context['user_id']) is None:
                waken_list[context['user_id']] = {'time': context['time']}
                if context['sender'].get('card') is None:
                    waken_list[context['user_id']]['nickname'] = context['sender']['nickname']
                else:
                    waken_list[context['user_id']]['nickname'] = context['sender']['card']
                waken_num += 1
                if waken_num == 1:
                    await bot.send(context, "获得成就：早起冠军")
                return {'reply': f"你是第{waken_num:d}起床的少年。"}
            else:
                return {'reply': f"你不是起床过了吗？"}

        elif message == 'wan':
            if waken_list.get(context['user_id']) is None:
                return {'reply': 'Pia!<(=ｏ ‵-′)ノ☆ 不起床就睡，睡死你好了～'}
            sleep_time = datetime.fromtimestamp(context['time'])
            wake_time = datetime.fromtimestamp(waken_list[context['user_id']]['time'])
            del waken_list[context['user_id']]
            duration = sleep_time - wake_time
            return {'reply': '今日共清醒{}秒，辛苦了'.format(
                str(duration).replace(':', '小时', 1).replace(':', '分', 1)
            )}

        elif message == 'zaoguys':
            waken_list_sorted = sorted(waken_list.items(), key=lambda value: value[1]['time'])
            now = datetime.now()
            msg = ""
            index = 1
            for person in waken_list_sorted:
                waken_time = datetime.fromtimestamp(person[1]['time'])
                waken_date = date.fromtimestamp(person[1]['time'])
                duration = now - waken_time
                if duration > timedelta(hours=24):
                    del waken_list[person[0]]
                if waken_date == today_date:
                    msg += f"\n{index}. {person[1]['nickname']}, {waken_time.hour:02d}:{waken_time.minute:02d}"
                    index += 1
            if msg == "":
                return {'reply': 'o<<(≧口≦)>>o 还没人起床'}
            return {'reply': msg}

        elif message == 'flush':
            if context['sender'].get('role') == 'owner' or 'admin':
                waken_list.clear()
                waken_num = 0
                repeat_mode = 0
                today_date = date.today()
                return {'reply': "咱也不知道发生了什么，咱也不敢问。"}
            else:
                return {'reply': "你没有权限o(≧口≦)o"}

        elif message == 'fudu' and (context['sender'].get('role') == 'owner' or 'admin'):
            if repeat_mode == 0:
                repeat_mode = 1
                return {'reply': "复读模式已开启(๑•̀ㅂ•́)و✧"}
            else:
                repeat_mode = 0
                return {'reply': "复读模式已关闭～(　TロT)σ"}

        else:
            return {'reply': '听不懂<(=－︿－=)>'}

    elif repeat_mode:
        return {'reply': context['message'], 'at_sender': False}

bot.run(host='0.0.0.0', port=8080)
