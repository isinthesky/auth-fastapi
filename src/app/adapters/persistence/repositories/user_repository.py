from sqlalchemy.ext.asyncio import AsyncSession
from src.app.core.ports.user_port import UserRepositoryPort
from src.app.core.domain.entities.user import UserEntity
from ..models.user import UserModel
from ..mappers.user_mapper import UserMapper

class UserRepository(UserRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.mapper = UserMapper()

    async def save(self, user: UserEntity) -> UserEntity:
        user_dict = self.mapper.to_model(user)
        db_user = UserModel(**user_dict)
        self.session.add(db_user)
        await self.session.commit()
        return self.mapper.to_entity(db_user) 