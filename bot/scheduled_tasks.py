from apscheduler.schedulers.background import BackgroundScheduler
from bot.utils import send
from bot.db import get_db
from bot.context import GroupContext
from datetime import date
import time


def init_background_tasks(app):
    apsched = BackgroundScheduler()
    apsched.add_job(ky_reminder, args=[app], trigger='cron', hour=12, minute=0)
    apsched.add_job(ghs_reminder, args=[app], trigger='cron', hour=21, minute=30)
    apsched.start()


def ky_reminder(app):
    with app.app_context():
        c = get_db()
        c.execute('BEGIN EXCLUSIVE')
        mutex = c.execute("select * from misc where key = 'mutex'").fetchone()
        if mutex is None:
            c.execute("insert into misc values ('mutex', '1')")
            remind_needed = 1
        elif mutex['value'] == '0':
            c.execute("update misc set value = '1' where key = 'mutex'")
            remind_needed = 1
        else:
            remind_needed = 0
        c.commit()  # end of exclusive transaction

        if remind_needed:
            data = c.execute('select * from misc where key = "ky_date"').fetchone()
            if data is None:
                send(GroupContext.build(group_id=app.config["KY_NOTIFY_GROUP"]),
                     message="管理员还未设定考研时间，使用 /setky 设定考研时间")
            ky_date_str = data['value']
            ky_date = date(int(ky_date_str[:4]), int(ky_date_str[4:6]), int(ky_date_str[6:]))
            days_to_ky = (ky_date - date.today()).days
            send(GroupContext.build(group_id=app.config["KY_NOTIFY_GROUP"]),
                 message=f"[CQ:at,qq=all] 距离{ky_date_str[:4]}年度研究生考试还有{days_to_ky}天")

            time.sleep(1)  # 为了防止过早执行完而导致其他 worker 继续执行

            c.execute("update misc set value = '0' where key = 'mutex'")
            c.commit()


def ghs_reminder(app):
    with app.app_context():
        c = get_db()
        data = c.execute('select * from misc where key = "last_ghs_date"').fetchone()
        if data is None:
            return
        last_ghs_date = data['value']
        period = (date.today() - date.fromisoformat(last_ghs_date)).days
        if period > 0:
            send(GroupContext.build(group_id=app.config["GHS_NOTIFY_GROUP"]),
                 message=f"[CQ:at,qq=all] 提醒：距离上次 ghs 已经过去了{period}天。")
        else:
            return
