import sqlite3
from datetime import date

conn = sqlite3.connect("database.db")
c = conn.cursor()

def init_database():
    c.execute("select * from sqlite_master where type='table' and name='waken_list'")
    if c.fetchall() == []:
        print("Initialing database")
        c.execute('''create table waken_list
        (id integer primary key,
        wake_timestamp integer, 
        wake_time text,
        nickname text,
        waken_num integer)
        ''')
        c.execute('''create table wake_history
        (id integer,
        wake_time text,
        sleep_time text
        )
        ''')
        c.execute('''create table log
        (message text,
        sender_nickname text,
        sender_id integer,
        timestamp integer,
        time text)
        ''')
        c.execute('''create table treehole
        (message text,
        timestamp integer,
        time text,
        sender_nickname text,
        sender_id integer)
        ''')

def init_waken_num():
    today_date = date.today()
    c.execute("SELECT wake_timestamp, waken_num FROM waken_list ORDER BY wake_timestamp DESC LIMIT 1")
    res = c.fetchone()
    if (res is None) or (today_date != date.fromtimestamp(res[0])):
        return 0
    else:
        return res[1]