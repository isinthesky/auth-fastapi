import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "User"
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    user_type = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, default=func.now(), onupdate=func.now())
    google_id = Column(String(255), unique=True, nullable=True)
    facebook_id = Column(String(255), unique=True, nullable=True)
    naver_id = Column(String(255), unique=True, nullable=True)
    tasks = relationship("Task", back_populates="user")
    state = Column(Integer, default=1, nullable=False)  # 1: enable, 2: hide, 0: disable


class TokenModel(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    access_token_expires = Column(DateTime, nullable=False)
    refresh_token_expires = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    revoked_at = Column(DateTime, nullable=True)
