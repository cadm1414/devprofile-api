from app.context.identity.domain.repositories.user_repository_interface import IUserRepository
from app.context.identity.domain.models.user_model import User
from app.context.identity.api.schemas.user_schema import UserUpdate
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

class UpdateUserUseCase:
    def __init__(self, user_repo: IUserRepository, db: Session):
        self.user_repo = user_repo
        self.db = db

    def execute(self, user_id: int, user_data: UserUpdate) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
                
        data_to_update = user_data.dict(exclude_unset=True)
        updated_user = self.user_repo.update(user, data_to_update)
        return updated_user
