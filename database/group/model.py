from datetime import datetime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, Float, Integer, DateTime, Date, Boolean

from database import Base

class Group(Base):
    __tablename__ = 'group'

    id   = Column(String, primary_key=True)
    name = Column(String)

    def __str__(self) -> str:
        return f'【{self.id}】{self.name}'

class GroupLocation(Base):
    __tablename__ = 'group_location'

    group_id       = Column(String, ForeignKey('group.id'), primary_key=True)
    brief          = Column(String)
    city_code      = Column(String)
    city           = Column(String)
    province       = Column(String)
    district       = Column(String)
    north_latitude = Column(Float)
    east_longitude = Column(Float)

    group          = relationship('Group', backref=backref("location", uselist=False))

    def __str__(self) -> str:
        return f'【{self.group_id}】{self.brief}'

class GroupMessage(Base):
    __tablename__ = 'group_message'

    id         = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(String,  index=True)
    qq_id      = Column(String,  index=True)
    group_id   = Column(String,  ForeignKey('group.id'))
    message    = Column(String)
    datetime   = Column(DateTime, default=datetime.now)

    group      = relationship('Group', backref=backref("messages"))

class GroupNotice(Base):
    __tablename__ = 'notice'

    id       = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(String,  ForeignKey('group.id'))
    title    = Column(String)
    date     = Column(Date,    index=True)
    fixed    = Column(Boolean)
    congratulations = Column(String)

    group      = relationship('Group', backref=backref("notices"))
