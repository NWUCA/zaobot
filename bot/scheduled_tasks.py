from apscheduler.schedulers.background import BackgroundScheduler
from bot.utils import send
from bot.db import get_db
from bot.context import GroupContext
from datetime import date


def init_background_tasks(app):
    apsched = BackgroundScheduler()
    apsched.add_job(ky_reminder, args=[app], trigger='cron', hour=12, minute=0)
    apsched.add_job(ghs_reminder, args=[app], trigger='cron', hour=21, minute=30)
    apsched.start()


def ky_reminder(app):
    with app.app_context():
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
