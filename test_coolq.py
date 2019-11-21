import pytest
from coolq import handle_msg
from datetime import datetime, time, date, timedelta

import json

def test_mytest():
    waken_list = {}
    today_date = date.today()
    waken_num = 0
    repeat_mode = 0
    with open('test.json', 'r') as f:
        s = f.read()
    data = json.loads(s)
    assert 1