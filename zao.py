"""
A simple plugin to record waken people and return order of waking.
"""
import logging
from . import TimerBot
from datetime import datetime, date
from dateutil.parser import parse as parse_date
from threading import Lock
from redis_variable import RedisVariable

logger = logging.getLogger(__name__)


class ZaoBot(TimerBot):
    def __init__(self, *args, **kwargs):
        self.new_day()
        # map id to Name
        self.guys_mapping = RedisVariable('zaobot:guys_mapping')
        self.lock = Lock()
        self.verbose_option = RedisVariable('zaobot:verbose_option')
        super().__init__(*args, **kwargs)

    def _verbose_chat(self, chat):
        verbose = self.verbose_option.hget(chat.id)
        logger.debug('verbose_chat: result from redis is {}'.format(verbose))
        if verbose is not None:
            return verbose.decode(encoding='UTF-8').lower() in ('yes', 'true', 'on')
        else:
            # default to verbose
            return True

    def _list_guys(self, waken_guys):
        '''
        return list of guys as tuple(`name`, `time`) which is sorted by date
        '''
        result = waken_guys.zrange(0, -1, withscores=True)
        logger.debug('list_guys: result from redis is {}'.format(result))

        # Transform result from redis ( (timestamp(byte), id(byte)) )
        # to result we need ( (name(str), time(datetime)) )
        def trans_func(id_timestamp):
            uid, timestamp = id_timestamp
            name = self.guys_mapping.hget(int(uid)).decode(encoding='UTF-8')
            logger.debug('list_guys: id -> name {}:{}'.format(uid, name))
            logger.debug('type of name: {}'.format(type(name)))
            time = datetime.fromtimestamp(int(timestamp))
            return (name, time)

        ret = map(trans_func, result)
        # logger.debug('list_guys: result after map is {}'.format(list(ret)))
        return list(ret)

    def _who(self, message):
        if message.text.startswith('/zaobug'):
            return "虫子"
        elif message.text.startswith('/zaobird'):
            return "鸟儿"
        elif message.text.startswith('/zaosheep'):
            return "小羊羔"
        else:
            return "少年"

    def _zaoText(self, message):
        if message.text.startswith('/zaobug'):
            return ",然后被鸟儿吃掉。"
        elif message.text.startswith('/zaobird'):
            return "然后被大鹰吃掉。"
        elif message.text.startswith('/zaosheep'):
            return "然后被萌狼吃掉。"
        else:
            return ""

    def new_day(self):
        today = str(date.today())
        self.waken_guys = RedisVariable('zaobot:waken_guys:{}'.format(today))
        self.sleep_guys = RedisVariable('zaobot:sleep_guys:{}'.format(today))

    def save_user(self, user):
        '''
        save name of user to redis
        '''
        if user.last_name is None:
            name = user.first_name
        else:
            name = '{} {}'.format(user.first_name, user.last_name)
        self.guys_mapping.hset(user.id, name)

    def bind(self):
        @self.sched.scheduled_job('cron', hour='5')
        def clear_guys():
            self.new_day()

        @self.bot.message_handler(commands=['option'])
        def option(message):
            tmp = ZaoBot.retrieve_args(message)
            if tmp is None:
                return

            args = tmp.split(' ')

            if args[0] == 'verbose':
                if len(args) == 1:
                    self.bot.send_message(
                        message.chat.id,
                        self._verbose_chat(message.chat))
                else:
                    self.verbose_option.hset(message.chat.id, args[1])

        @self.bot.message_handler(commands=['zaoguys', 'zaobirds', 'zaobugs', 'zaosheeps'])
        def list_guys(message):
            date_str = ZaoBot.retrieve_args(message)
            if date_str is None:
                waken_guys = self.waken_guys
            else:
                try:
                    date = parse_date(date_str)
                    waken_guys = RedisVariable(
                        'zaobot:waken_guys:{}'.format(date.date()))
                except ValueError:
                    self.bot.reply_to(message, '听不懂<(=－︿－=)>')
                    return
            sorted_guys = self._list_guys(waken_guys)
            logger.debug('sorted_guys is {}'.format(list(sorted_guys)))
            prefix = ""
            if message.text.startswith('/zaobugs'):
                prefix = "被鸟儿吃掉的虫子:\n"
            elif message.text.startswith('/zaobirds'):
                prefix = "被大鹰吃掉的鸟儿:\n"
            elif message.text.startswith('/zaosheeps'):
                prefix = "被萌狼吃掉的小羊羔:\n"

            if sorted_guys:
                self.bot.send_message(
                    message.chat.id,
                    prefix + '\n'.join(
                        map(
                            lambda i_guy: '{}. {}, {:%H:%M}'.format(
                                i_guy[0] + 1, *i_guy[1]),
                            enumerate(sorted_guys)
                        )
                    ))
            else:
                self.bot.reply_to(message, 'o<<(≧口≦)>>o 还没人起床')

        @self.bot.message_handler(commands=['wan'])
        def wan_handler(message):
            self.save_user(message.from_user)

            waken_time = self.waken_guys.zscore(message.from_user.id)
            first_sleep = self.sleep_guys.zscore(message.from_user.id)
            if first_sleep is None:
                # This is the first time of today to sleep
                self.sleep_guys.zadd(message.date, message.from_user.id)

            # Response
            if self._verbose_chat(message.chat):
                if waken_time is None:
                    self.bot.reply_to(
                        message, "Pia!<(=ｏ ‵-′)ノ☆ 不起床就睡，睡死你好了～")
                elif first_sleep is None:
                    waken_datetime = datetime.fromtimestamp(int(waken_time))
                    sleep_datetime = datetime.fromtimestamp(message.date)
                    duration = sleep_datetime - waken_datetime
                    self.bot.reply_to(
                        message,
                        "今日共清醒{}秒，辛苦了".format(
                            str(duration).replace(':', '小时', 1).replace(':', '分', 1)))
                else:
                    first_sleep_datetime = datetime.fromtimestamp(int(first_sleep))
                    this_sleep_datetime = datetime.fromtimestamp(message.date)
                    duration = this_sleep_datetime - first_sleep_datetime
                    self.bot.reply_to(
                        message,
                        "关机失败{}秒 Pia!<(=ｏ ‵-′)ノ☆".format(
                            str(duration).replace(':', '小时', 1).replace(':', '分', 1)))

        @self.bot.message_handler(commands=['zao', 'zaobug', 'zaobird', 'zaosheep'])
        def zao_handler(message):
            self.save_user(message.from_user)

            with self.lock:
                # There seems no way to determine whether an element in
                # sorted set except trying to retrieve it.
                rank = self.waken_guys.zrank(message.from_user.id)
                index = self.waken_guys.zcard()
                if rank is None:
                    self.waken_guys.zadd(message.date, message.from_user.id)
                    rewaken = False
                else:
                    rewaken = True

            # Send response
            if self._verbose_chat(message.chat):
                if rewaken:
                    self.bot.reply_to(message, "Pia!<(=ｏ‵-′)ノ☆  你不是起床过了吗?")
                else:
                    if index == 0:
                        self.bot.reply_to(message, "✔ 获得成就[最早起床]")
                    else:
                        self.bot.send_message(
                            message.chat.id,
                            "你是第{:d}起床的{}{}".format(
                                index + 1, self._who(message), self._zaoText(message))
                        )