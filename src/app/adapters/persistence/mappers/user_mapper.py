from src.app.core.domain.entities.user import UserEntity
from ..models.user import UserModel

class UserMapper:
    @staticmethod
    def to_entity(model: UserModel) -> UserEntity:
        return UserEntity(
            user_id=model.user_id,
            name=model.name,
            email=model.email,
            user_type=model.user_type,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login=model.last_login,
            state=model.state,
            social_accounts=model.social_accounts
        )

    @staticmethod
    def to_model(entity: UserEntity) -> dict:
        return {
            "user_id": entity.user_id,
            "name": entity.name,
            "email": entity.email,
            "user_type": entity.user_type,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
            "last_login": entity.last_login,
            "state": entity.state,
            "social_accounts": entity.social_accounts
        } 