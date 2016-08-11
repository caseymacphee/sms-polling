import uuid
from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm.exc import NoResultFound

from sms_poll.database import Base, db_session
from sms_poll.log import log


class Vote(Base):
    __tablename__ = 'poll'
    id = Column(String(18))
    number = Column(String(18), primary_key=True, unique=True)
    vote = Column(Integer)

    def __init__(self, number, vote):
        self.id = uuid.uuid4().hex
        self.value = number
        self.vote = vote
