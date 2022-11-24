from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, Boolean

from database import Base
from database.group.model import Group

class Task(Base):
    __tablename__ = 'task'

    key    = Column(String, primary_key=True)
    usable = Column(Boolean)

    def __str__(self) -> str:
        if self.usable:
            return self.key
        return '【失效】' + self.key

class CronGroupTask(Base):
    __tablename__ = 'cron_group_task'

    id          = Column(Integer, primary_key=True, autoincrement=True)
    brief       = Column(String,  nullable=True)

    group_id    = Column(Integer, ForeignKey('group.id'), nullable=True)
    task_key    = Column(String,  ForeignKey('task.key'), nullable=True)

    year        = Column(String, default='*', nullable=True)
    month       = Column(String, default='*', nullable=True)
    day         = Column(String, default='*', nullable=True)
    day_of_week = Column(String, default='*', nullable=True)
    hour        = Column(String, default='*', nullable=True)
    minute      = Column(String, default='0', nullable=True)
    second      = Column(String, default='0', nullable=True)

    addition    = Column(String, nullable=True)

    group: Group = relationship('Group', backref=backref("cron_group_tasks"))
    task:  Task  = relationship('Task',  backref=backref("cron_group_tasks"))

    def __str__(self) -> str:
        return self.brief

    @property
    def param(self) -> dict:
        return {
            'year':        self.year,
            'month':       self.month,
            'day':         self.day,
            'day_of_week': self.day_of_week,
            'hour':        self.hour,
            'minute':      self.minute,
            'second':      self.second,
        }




    