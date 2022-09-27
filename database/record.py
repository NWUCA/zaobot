from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import DateTime, String, Integer
from database import Base

class GroupMessage(Base):
    __tablename__ = 'group_message'
    id = Column(Integer, primary_key=True)
    group_id = Column(String(12), index=True)
    msg = Column(String)
    datetime = Column(DateTime, default=datetime.now)