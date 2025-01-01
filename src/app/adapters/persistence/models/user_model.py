from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from src.app.adapters.persistence.base import Base
from datetime import datetime, timezone
import uuid

class UserModel(Base):
    __tablename__ = "users"
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    user_type = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    last_login = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    social_accounts = Column(JSON, nullable=True)
    state = Column(Integer, default=1, nullable=False)