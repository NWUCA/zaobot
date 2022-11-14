from datetime import datetime

from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, JSON, DateTime, Date

from database import Base

class GroupGridWeather3d(Base):
    __tablename__ = 'group_grid_weather_3d'
    
    group_id      = Column(String, ForeignKey('group.id'), primary_key=True)
    raw_json      = Column(JSON)
    request_time  = Column(DateTime, index=True, default=datetime.now)
    update_time   = Column(DateTime, index=True)
    forecast_date = Column(Date,     index=True)

    group         = relationship('Group', backref=backref("grid_weather_3d"))

    def __str__(self) -> str:
        return f'【{self.group_id}】{self.update_time}'

