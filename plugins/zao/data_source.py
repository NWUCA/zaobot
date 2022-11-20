from datetime import datetime, timedelta

def get_yesterday_4_clock() -> datetime:
    now = datetime.now()
    t = datetime(now.year, now.month, now.day, 4, 0, 0)
    if t > now:
        t = t - timedelta(days=1)
    return t
