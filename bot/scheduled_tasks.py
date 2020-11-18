from datetime import date
import atexit
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
from bot.utils import send
from bot.db import get_db
from bot.context import GroupContext


class ModifiedBackgroundScheduler(BackgroundScheduler):
    def __init__(self, app, **options):
        self.app = app  # flask app
        super().__init__(**options)

    def add_job(self, func, *_args, **_kwargs):  # args and kwargs are already used
        """
        对每个 job 添加 app_context
        """
        def wrapper(*args, **kwargs):
            with self.app.app_context():
                func(self.app, *args, **kwargs)

        super().add_job(wrapper, *_args, **_kwargs)


def init_background_tasks(app):
    """
    不同 job 之间的间隔应大于 1 分钟, 否则会导致某些 job 不被执行.
    job 的执行函数第一个参数为当前的 app
    """
    with app.app_context():
        c = get_db()
        c.execute('BEGIN EXCLUSIVE')
        mutex = c.execute("select * from misc where key = 'mutex'").fetchone()
        if mutex is None:
            c.execute("insert into misc values ('mutex', '1')")
            start_flag = 1
        elif mutex['value'] == '0':
            c.execute("update misc set value = '1' where key = 'mutex'")
            start_flag = 1
        else:
            start_flag = 0
        c.commit()  # end of exclusive transaction
    if start_flag:
        apsched = ModifiedBackgroundScheduler(app)
        apsched.add_job(ky_reminder, trigger='cron', hour=12, minute=0, id='ky_reminder')
        apsched.add_job(ghs_reminder, trigger='cron', hour=21, minute=30, id='ghs_reminder')
        apsched.start()

        def unlock():
            with app.app_context():
                try:
                    c = get_db()
                    c.execute("update misc set value = '0' where key = 'mutex'")
                    c.commit()
                except sqlite3.OperationalError:
                    pass

        atexit.register(unlock)

        return apsched
    return None


def ky_reminder(app):
    c = get_db()
    data = c.execute('select * from misc where key = "ky_date"').fetchone()
    if data is None:
        send(GroupContext.build(group_id=app.config["KY_NOTIFY_GROUP"]),
             message="管理员还未设定考研时间，使用 /setky 设定考研时间")
    ky_date_str = data['value']
    ky_date = date(int(ky_date_str[:4]), int(ky_date_str[4:6]), int(ky_date_str[6:]))
    days_to_ky = (ky_date - date.today()).days
    send(GroupContext.build(group_id=app.config["KY_NOTIFY_GROUP"]),
         message=f"[CQ:at,qq=all] 距离{ky_date_str[:4]}年度研究生考试还有{days_to_ky}天")


def ghs_reminder(app):
    c = get_db()
    data = c.execute('select * from misc where key = "last_ghs_date"').fetchone()
    if data is None:
        return
    last_ghs_date = data['value']
    period = (date.today() - date.fromisoformat(last_ghs_date)).days
    if period > 0:
        send(GroupContext.build(group_id=app.config["GHS_NOTIFY_GROUP"]),
             message=f"提醒：距离上次 ghs 已经过去了{period}天。")
    else:
        return
