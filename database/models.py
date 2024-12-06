from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String
from .db_session import Base

class AdminSettings(Base):
    __tablename__ = "admin_settings"

    id = Column(Integer, primary_key=True, index=True)
    hashed_password = Column(String, nullable=False)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    role = Column(Integer, default=1) 
    balance = Column(Float, default=0.0)

class Bank(Base):
    __tablename__ = 'banks'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    added_by = Column(String)

class Card(Base):
    __tablename__ = 'cards'

    id = Column(Integer, primary_key=True, index=True)
    bank_id = Column(Integer, ForeignKey('banks.id'))
    bank_name = Column(String)
    last_four_digits = Column(String, index=True)
    daily_limit = Column(Float)
    remaining_limit = Column(Float)
    added_by = Column(String)

    bank = relationship("Bank")

