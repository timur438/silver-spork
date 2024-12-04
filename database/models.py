from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String
from .db_session import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    role = Column(Integer, default=1) 

class Bank(Base):
    __tablename__ = 'banks'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class Card(Base):
    __tablename__ = 'cards'

    id = Column(Integer, primary_key=True, index=True)
    bank_id = Column(Integer, ForeignKey('banks.id'))
    last_four_digits = Column(String, index=True)
    daily_limit = Column(Float)
    remaining_limit = Column(Float)
    current_balance = Column(Float)

    bank = relationship("Bank")

