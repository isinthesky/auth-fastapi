from datetime import datetime, timezone
from src.app.core.domain.entities.user import UserEntity
from ..models.user_model import UserModel
from typing import Optional

def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if not dt:
        return None
    if dt.tzinfo is None:
        # naive -> utc로 맞춤
        return dt.replace(tzinfo=timezone.utc)
    # 이미 다른 tzinfo가 있다면, 필요 시 UTC로 변환: dt.astimezone(timezone.utc)
    return dt


class UserMapper:
    @staticmethod
    def to_entity(model: UserModel) -> UserEntity:
        return UserEntity(
            user_id=model.user_id,
            name=model.name,
            email=model.email,
            user_type=model.user_type,
            created_at=ensure_utc(model.created_at),
            updated_at=ensure_utc(model.updated_at),
            last_login=ensure_utc(model.last_login),
            state=model.state,
            social_accounts=model.social_accounts
        )

    @staticmethod
    def to_model(entity: UserEntity) -> UserModel:
        return UserModel(
            user_id=entity.user_id,
            name=entity.name,
            email=entity.email,
            user_type=entity.user_type,
            created_at=entity.created_at.replace(tzinfo=None) if entity.created_at else None,
            updated_at=entity.updated_at.replace(tzinfo=None) if entity.updated_at else None,
            last_login=entity.last_login.replace(tzinfo=None) if entity.last_login else None,
            state=entity.state,
            social_accounts=entity.social_accounts
        )