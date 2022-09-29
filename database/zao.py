from datetime import datetime
from sqlalchemy import Column, DateTime, String, Integer
from sqladmin import ModelView
from database import Base

class ZaoGuy(Base):
    __tablename__ = 'zao_guy'
    # id           = Column(BigInteger, primary_key=True, autoincrement=True)
    # sqlite BigInt can not auto increment
    id           = Column(Integer,    primary_key=True, autoincrement=True)
    qq_id        = Column(String(16), index=True)
    group_id     = Column(String(16), index=True)
    nickname     = Column(String)
    zao_datetime = Column(DateTime,   default=datetime.now)
    wan_datetime = Column(DateTime,   default=None, nullable=True)


class ZaoGuyAdmin(ModelView, model=ZaoGuy):
    column_list = [
        ZaoGuy.id,
        ZaoGuy.qq_id,
        ZaoGuy.group_id,
        ZaoGuy.nickname,
        ZaoGuy.zao_datetime,
        ZaoGuy.wan_datetime,
    ]


