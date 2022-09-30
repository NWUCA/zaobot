from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import String, Integer, Date, Boolean
from sqladmin import ModelView
from database import Base

class Notice(Base):
    __tablename__ = 'notice'
    id       = Column(Integer,    primary_key=True, autoincrement=True)
    group_id = Column(String(16), index=True)
    title    = Column(String)
    date     = Column(Date,       index=True)
    fixed    = Column(Boolean)
    congratulations = Column(String)

class NoticeAdmin(ModelView, model=Notice):
    column_list = [
        Notice.id,
        Notice.group_id,
        Notice.title,
        Notice.date,
        Notice.fixed,
    ]
