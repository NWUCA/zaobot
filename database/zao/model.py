from datetime import datetime
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import DateTime, String, Integer

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