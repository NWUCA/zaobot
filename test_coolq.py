import pytest
from coolq import handle_msg
from datetime import datetime, time, date, timedelta

import json

@pytest.fixture
def data():
    with open("test_data.json", "r") as f:
        return json.load(f)

def test_mytest():
    waken_list = {}
    today_date = date.today()
    waken_num = 0
    repeat_mode = 0
    with open('test.json', 'r') as f:
        s = f.read()
    data = json.loads(s)
    assert 1

def test_dir(data):
    print(data)
    # print(data())
    assert handle_msg(data[0]) == {'reply': '你是第1起床的少年。'}
    assert 0