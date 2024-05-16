from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)

    devices = relationship("Device", back_populates="user")
    ostrich_token = relationship("OstrichToken", back_populates="user")
    wotc_token = relationship("WotcToken", back_populates="user")


class WotcToken(Base):
    __tablename__ = "wotc_tokens"

    id = Column(String, primary_key=True)

    access_token = Column(String)
    expires_in = Column(Integer)
    refresh_token = Column(String)

    user_id = Column(String, ForeignKey("users.id"))
    user = relationship("User", back_populates="wotc_token")


class OstrichToken(Base):
    __tablename__ = "ostrich_tokens"

    id = Column(String, primary_key=True)

    access_token = Column(String)
    expires_in = Column(Integer)
    refresh_token = Column(String)

    user_id = Column(String, ForeignKey("users.id"))
    user = relationship("User", back_populates="ostrich_token")


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    communication_token = Column(String)

    user_id = Column(String, ForeignKey("users.id"))
    user = relationship("User", back_populates="devices")
