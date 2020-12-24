"""
zaobot的所有指令
"""
import random
from datetime import date, datetime, timedelta

import requests

from bot.db import get_db
from bot.utils import reply, average_rest_time, send
from bot.utils import xiuxian_level, start_xiuxian
from bot.utils import admin_required, private_message_only
from bot.utils import query_ky
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
        ans = requests.get('https://yesno.wtf/api/').json()
        resp = [
            {
                "type": "reply",
                "data": {
                    "id": self.context.message_id
                }
            },
            {
                "type": "text",
                "data": {
                    "text": ans['answer']
                }
            },
            {
                "type": "image",
                "data": {
                    "file": ans['image']
                }
            }
        ]
        send(self.context, resp)

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
        c.execute("insert into treehole values (?,?,?,?,?,'say')",
                  (secret, timestamp, time, self.context.name, self.context.user_id))
        c.commit()
        return reply("我记在脑子里啦！")

    def dig(self):
        """随机从树洞取一条消息"""
        c = get_db()
        length = c.execute('select count(*) from treehole').fetchone()[0]
        rand = random.randrange(length)
        secret = c.execute(f'select message from treehole limit 1 offset {rand}').fetchone()['message']
        return reply("某个人说：" + secret, at_sender=False)

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

    def wyy(self):
        """网抑云"""
        r = requests.get(f'https://nd.2890.ltd/api/?format=text&id={random.randrange(int(1e9))}')
        return reply(r.text, at_sender=False)

    @admin_required
    def setky(self):
        """
        设置考研日期
        """
        c = get_db()
        try:
            ky_date_str = self.context.args[0]
            date(int(ky_date_str[:4]), int(ky_date_str[4:6]), int(ky_date_str[6:]))
            if len(ky_date_str) != 8:
                raise ValueError
            data = c.execute("select * from misc where key = 'ky_date'").fetchone()
            if data is None:
                c.execute("insert into misc values ('ky_date', ?)", (ky_date_str,))
            else:
                c.execute("update misc set value = ? where key = 'ky_date'", (ky_date_str,))
            c.commit()
            return reply("设置成功")
        except (IndexError, ValueError):
            return reply("考研时间格式必须为yyyyMMdd")

    def ky(self):
        """
        查询距离考研的天数
        """
        return reply(query_ky())

    def q(self):
        """
        按照知识图谱，回答一个问题
        """
        try:
            question = self.context.args[0]
        except IndexError:
            return reply("你必须问点什么。")

        r = requests.get(f'https://api.ownthink.com/bot?spoken={question}')
        try:
            ans = r.json()['data']['info']['text']
            return reply(ans, at_sender=False)
        except (IndexError, KeyError):
            return reply("上游似乎出锅了QAQ，或者你输入了奇怪的东西WWW")
