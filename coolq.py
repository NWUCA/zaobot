from cqhttp import CQHttp
import re
from datetime import datetime, date, timedelta
import random
import sqlite3
import init
from flask import g, current_app


def create_app(config=None):
    bot = CQHttp(api_root='http://127.0.0.1:5700/')
    app = bot.server_app
    app.config.from_mapping(
        DATABASE='database.db'
    )
    if config:
        # load the config if passed in
        app.config.from_mapping(config)

    return bot


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
    g.c = g.db.cursor()
    return g.c


def reply(msg, at_sender=True):
    now = datetime.now().timestamp()
    # 构造log所需的context
    log({'message': msg, 'sender': {'nickname': 'zaobot'}, 'time': now, 'user_id': 0})
    return {'reply': msg, 'at_sender': at_sender}


def remove_timeout_user(user_id, now, hour=12):
    c.execute(f'select wake_timestamp from waken_list where id ={user_id}')
    res = c.fetchone()  # res 为一个元组
    if res is None:
        return

    waken_time = datetime.fromtimestamp(res[0])
    now = datetime.fromtimestamp(now)
    duration = now - waken_time
    if duration > timedelta(hours=hour):
        c.execute(f'delete from waken_list where id ={user_id}')


@bot.on_message()
def handle_msg(context):
    global today_date, waken_num, repeat_mode
    if re.match('/', context['message']) is not None:
        message = context['message'][1:]
        message = message.split()
        command = message[0]
        args = message[1:]

        log(context)

        remove_timeout_user(context['user_id'], context['time'], 48)

        # 新的一天
        if date.fromtimestamp(context['time']) != today_date:
            today_date = date.fromtimestamp(context['time'])
            waken_num = 0

        if command == 'help':
            return reply('我的源码存放在：github.com/cjc7373/zaobot，尽情探索吧。')

        elif command == 'zao':
            remove_timeout_user(context['user_id'], context['time'])

            c.execute(f'select * from waken_list where id ={context["user_id"]}')
            res = c.fetchone()
            if res is None:
                waken_num += 1
                wake_timestamp = context['time']
                wake_time = datetime.fromtimestamp(context['time'])
                # 这么写会报错 sqlite3.OperationalError: near "08": syntax error 很奇怪
                # c.execute(f"insert into waken_list values ({context['user_id']}, {wake_timestamp}, "
                #           f"{wake_time}, {get_nickname(context)}, {waken_num})")
                inserted_data = (context['user_id'], wake_timestamp, wake_time, get_nickname(context), waken_num)
                c.execute("insert into waken_list values (?,?,?,?,?)", inserted_data)
                conn.commit()
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
            c.execute(f'select wake_timestamp from waken_list where id ={context["user_id"]}')
            res = c.fetchone()
            if res is None:
                return {'reply': 'Pia!<(=ｏ ‵-′)ノ☆ 不起床就睡，睡死你好了～'}
            sleep_time = datetime.fromtimestamp(context['time'])
            wake_time = datetime.fromtimestamp(res[0])
            duration = sleep_time - wake_time
            if duration < timedelta(minutes=30):
                return reply("你不是才起床吗？")
            else:
                c.execute(f"delete from waken_list where id ={context['user_id']}")
                return {'reply': '今日共清醒{}秒，辛苦了'.format(
                    str(duration).replace(':', '小时', 1).replace(':', '分', 1)
                )}

        elif command == 'zaoguys':
            c.execute(f'select nickname, wake_timestamp from waken_list')
            waken_list = c.fetchall()
            msg = ""
            index = 1
            for person in waken_list:
                waken_time = datetime.fromtimestamp(person[1])
                waken_date = date.fromtimestamp(person[1])
                if waken_date == today_date:
                    msg += f"\n{index}. {person[0]}, {waken_time.hour:02d}:{waken_time.minute:02d}"
                    index += 1
            if msg == "":
                return {'reply': 'o<<(≧口≦)>>o 还没人起床'}
            return {'reply': msg}

        elif command == 'flush':
            return flush_handler(context)

        elif command == 'fudu':
            return fudu_handler(context)

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
            timestamp = context['time']
            time = datetime.fromtimestamp(timestamp)
            c.execute(f"insert into treehole values "
                      f"{secret}, {timestamp}, {time}, {get_nickname(context)}, {context['user_id']})")
            conn.commit()
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


class admin_required:
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
def flush_handler(context):
    if context['user_id'] == 617175214:
        return reply("狗滑稽又来删库了(╯°Д°)╯︵ ┻━┻")
    global today_date, waken_num, repeat_mode
    c.execute("delete from waken_list")
    waken_num = 0
    repeat_mode = 0
    today_date = date.today()
    return {'reply': "清除数据成功。"}


def log(context):
    time = datetime.fromtimestamp(context['time'])
    inserted_data = (context['message'], get_nickname(context),
                     context['user_id'], context['time'], str(time))
    c.execute("insert into log values (?,?,?,?,?)", inserted_data)
    conn.commit()


def get_nickname(context):
    if context['sender'].get('card') is None:
        return context['sender']['nickname']
    else:
        return context['sender']['card']


if __name__ == "__main__":
    bot = create_app()

    # Deprecated
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    init.init_database(c)

    today_date = date.today()
    repeat_mode = 0
    waken_num = init.init_waken_num(c)
    bot.run(host='0.0.0.0', port=8080, debug=True)
