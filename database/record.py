from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import DateTime, String, Integer
from sqladmin import ModelView
from database import Base

class GroupMessage(Base):
    __tablename__ = 'group_message'
    id       = Column(Integer,    primary_key=True, autoincrement=True)
    qq_id    = Column(String(16), index=True)
    group_id = Column(String(16), index=True)
    message  = Column(String)
    datetime = Column(DateTime,   default=datetime.now)

class GroupMessageAdmin(ModelView, model=GroupMessage):
    column_list = [
        GroupMessage.id,
        GroupMessage.qq_id,
        GroupMessage.group_id,
        GroupMessage.message,
        GroupMessage.datetime,
    ]
