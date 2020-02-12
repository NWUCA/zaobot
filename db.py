from datetime import date
import sqlite3
from flask import g, current_app


def init_database():
    c = get_db()
    res = c.execute("select * from sqlite_master where type='table' and name='waken_list'").fetchone()
    if res is None:
        print("Initialing database")
        with current_app.open_resource('schema.sql', 'r') as f:
            c.executescript(f.read())
        c.commit()

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
    if 'db_connection' not in g:
        g.db_connection = sqlite3.connect(current_app.config['DATABASE'])
    # TODO use row factory
    return g.db_connection


def close_db(e=None):
    db_connection = g.pop('db_connection', None)

    if db_connection is not None:
        db_connection.close()