"""
zaobot的所有指令
"""
import random
from datetime import date, datetime, timedelta

import requests

from bot.db import get_db
from bot.utils import reply, average_rest_time
from bot.utils import xiuxian_level, start_xiuxian
from bot.utils import admin_required, private_message_only
from bot.context import Context


class Directive:
    def __init__(self, context: Context):
        self.context = context

    def help(self):
        """帮助"""
        directive = (i for i in dir(self) if (not i.startswith('__')) and i != "context")
        msg = "所有可用的命令如下:\n"
        for i in directive:
            msg += f"/{i}  "
            if getattr(self, i).__doc__ is not None:
                msg += getattr(self, i).__doc__.strip()
            msg += "\n"
        return reply(msg + '我的源码存放在：github.com/NWUCA/zaobot，尽情探索吧。')

    def zao(self):
        """起床"""
        c = get_db()

        today = date.fromtimestamp(self.context.time)

        current_user = c.execute('select * from rest_record where id = ? and wake_time like ?',
                                 (self.context.user_id, str(today) + "%")).fetchone()
        if current_user is None or date.fromtimestamp(current_user['wake_timestamp']) != today:
            last_user = c.execute(
                "SELECT wake_timestamp, waken_num FROM rest_record ORDER BY wake_timestamp DESC LIMIT 1").fetchone()
            if last_user is None or date.fromtimestamp(last_user['wake_timestamp']) != today:
                # 新的一天
                waken_num = 1
            else:
                waken_num = last_user['waken_num'] + 1
            wake_timestamp = self.context.time
            wake_time = datetime.fromtimestamp(self.context.time)
            inserted_data = (
                self.context.user_id, wake_timestamp, wake_time, self.context.name, waken_num, '', '')  # 注意顺序
            c.execute("insert into rest_record values (?,?,?,?,?,?,?)", inserted_data)
            c.commit()
            try:
                greeting = self.context.args[0]
            except IndexError:
                greeting = '少年'
            return reply(f"你是第{waken_num:d}起床的{greeting}。")
        elif current_user['sleep_timestamp'] != '':
            return reply("你不是睡了吗？")
        else:
            return reply("你不是起床过了吗？")

    def wan(self):
        """睡觉"""
        c = get_db()
        start_xiuxian(self.context)
        current_user = c.execute(f'select wake_timestamp from rest_record '
                                 f'where id ={self.context.user_id} ORDER BY wake_timestamp DESC LIMIT 1').fetchone()
        current_time = datetime.fromtimestamp(self.context.time)
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
                delay_minute = int(self.context.args[0])
                sleep_time = current_time + timedelta(minutes=delay_minute)
                duration += timedelta(minutes=delay_minute)
                msg += f"将在{delay_minute}分钟后睡觉。\n"
            except (IndexError, ValueError):
                sleep_time = current_time

            c.execute(
                "update rest_record set sleep_timestamp = ?, sleep_time = ? "
                "where id = ? and wake_timestamp = ?",
                (sleep_time.timestamp(), sleep_time, self.context.user_id, current_user['wake_timestamp']))
            c.commit()
            msg += '今日共清醒{}秒，辛苦了'.format(str(duration).replace(':', '小时', 1).replace(':', '分', 1))
            return reply(msg)

    def zaoguys(self):
        """获取起床列表"""
        c = get_db()
        today = date.fromtimestamp(self.context.time)
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

    def ask(self):
        """获取 Yes or No"""
        try:
            _ = self.context.args[0]
        except IndexError:
            return reply("说一个二元问题(´・ω・`)")
        if random.randrange(2) == 1:
            return reply("Yes")
        else:
            return reply("No")

    def say(self):
        """向树洞里说一句话"""
        c = get_db()

        try:
            self.context.args[0]
        except IndexError:
            return reply("你必须说点什么。")

        secret = " ".join(self.context.args)
        timestamp = self.context.time
        time = datetime.fromtimestamp(timestamp)
        c.execute("insert into treehole values (?,?,?,?,?)",
                  (secret, timestamp, time, self.context.name, self.context.user_id))
        c.commit()
        return reply("我记在脑子里啦！")

    def backdoor(self):
        c = get_db()
        msg = ""
        try:
            timestamp = self.context.message.replace("/backdoor ", "")
            res = c.execute(f"select * from treehole where timestamp = {timestamp}").fetchall()
            for i in res:
                msg += str(tuple(i)) + '\n'
        except IndexError:
            pass
        except Exception as e:
            msg = str(e)
        return reply(msg)

    def dig(self):
        """Under construction"""
        # total_length = r.llen('secrets')
        # rand = random.randrange(total_length)
        # secret = r.lrange('secrets', rand, rand)[0]
        # return reply("某个人说：" + secret, False)
        return reply("")

    @admin_required
    def flush(self):
        # c = get_db()
        # c.execute("delete from rest_record")
        return reply("清除数据成功。")

    @private_message_only
    def rest_statistic(self):
        """获取作息统计信息。"""
        c = get_db()
        rest_list = c.execute('select * from rest_record where id = ?', (self.context.user_id,)).fetchall()
        valid_record = [i for i in rest_list if i['sleep_time'] != '']
        msg = average_rest_time(valid_record, 7) + \
            average_rest_time(valid_record, 30) + \
            average_rest_time(valid_record, 365)
        if msg == "":
            return reply("暂无数据。")
        else:
            return reply(msg)

    def xiuxian_ranking(self):
        """修仙排行"""
        c = get_db()
        res = c.execute('select * from xiuxian_emulator order by exp desc limit 10').fetchall()
        if len(res) == 0:
            return reply('呜呼！仙道中落，世间竟无人修仙！')
        msg = ""
        for i, person in enumerate(res):
            msg += f"{i + 1}. {person['nickname']} {xiuxian_level[person['level']][0]}期 " \
                   f"经验{person['exp']}/{xiuxian_level[person['level']][1]}\n"
        return reply(msg, at_sender=False)

    def sxcx(self):  # sxcx 为拼音缩写
        """缩写查询"""
        try:
            word = self.context.args[0]
        except IndexError:
            return reply("你必须输入一个缩写。")

        data = {"text": word}
        r = requests.post('https://lab.magiconch.com/api/nbnhhsh/guess', json=data)
        try:
            r.json()[0]['name']
        except (IndexError, KeyError):
            return reply("上游似乎出锅了QAQ，或者你输入了奇怪的东西WWW")

        rtn = ''
        for data in r.json():
            word = data.get('name')
            trans = data.get('trans')
            if trans is None or trans == []:
                rtn += f"未找到{word}的解释。\n"
            else:
                rtn += f"{word} 可能是{','.join(trans)}的缩写。\n"
        rtn = rtn.strip()
        return reply(rtn, at_sender=False)

    def chp(self):
        """彩虹屁"""
        r = requests.get('https://chp.shadiao.app/api.php')
        return reply(r.text, at_sender=False)

    def nmsl(self):
        """彩虹屁"""
        r = requests.get('https://chp.shadiao.app/api.php')
        return reply(r.text, at_sender=True)
