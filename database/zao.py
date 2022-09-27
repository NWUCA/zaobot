from datetime import datetime
from sqlalchemy import Column, DateTime, String, Boolean
from database import Base

class ZaoBoy(Base):
    __tablename__ = 'zao_boy'
    qq_id = Column(String(12), primary_key=True)
    qq_nickname = Column(String)
    zao_datetime = Column(DateTime, default=datetime.now)
    has_wan = Column(Boolean, default=False)
