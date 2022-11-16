from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, Boolean

from database import Base

class Task(Base):
    __tablename__ = 'task'

    key    = Column(String, primary_key=True)
    usable = Column(Boolean)

    def __str__(self) -> str:
        return self.key


class CronTrigger(Base):
    __tablename__ = 'cron_trigger'

    id          = Column(Integer, primary_key=True, autoincrement=True)
    brief       = Column(String)
    year        = Column(String, default='*', nullable=True)
    month       = Column(String, default='*', nullable=True)
    day         = Column(String, default='*', nullable=True)
    day_of_week = Column(String, default='*', nullable=True)
    hour        = Column(String, default='*', nullable=True)
    minute      = Column(String, default='0', nullable=True)
    second      = Column(String, default='0', nullable=True)

    def __str__(self) -> str:
        return self.brief


class GroupCronTriggerTask(Base):
    __tablename__ = 'group_schedule_cron'

    id              = Column(Integer, primary_key=True, autoincrement=True)
    group_id        = Column(Integer, ForeignKey('group.id'))
    task_key        = Column(String,  ForeignKey('task.key'))
    cron_trigger_id = Column(Integer, ForeignKey('cron_trigger.id'))

    group        = relationship('Group',       backref=backref("cron_trigger_task"))
    task         = relationship('Task',        backref=backref("cron_trigger_task"))
    cron_trigger = relationship('CronTrigger', backref=backref("cron_trigger_task"))



    