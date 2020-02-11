from datetime import date
import sqlite3
from flask import g, current_app


def init_database(cursor):
    c = cursor
    c.execute("select * from sqlite_master where type='table' and name='waken_list'")
    if c.fetchall() == []:
        print("Initialing database")
        with open('schema.sql', 'r') as f:
            c.executescript(f.read())

def init_waken_num(cursor):
    c = cursor
    today_date = date.today()
    c.execute("SELECT wake_timestamp, waken_num FROM waken_list ORDER BY wake_timestamp DESC LIMIT 1")
    res = c.fetchone()
    if (res is None) or (today_date != date.fromtimestamp(res[0])):
        return 0
    else:
        return res[1]


def get_db():
    if 'db' not in g:
        g.db_connection = sqlite3.connect(current_app.config['DATABASE'])
    return g.db_connection