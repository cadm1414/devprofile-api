from app.context.identity.domain.repositories.user_repository_interface import IUserRepository
from app.context.identity.domain.models.user_model import User
from app.context.identity.api.schemas.user_schema import UserUpdate
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

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
        
        try:
            updated_user = self.user_repo.update(user, data_to_update)
            return updated_user
        except IntegrityError as e:
            self.db.rollback()
            if "ix_users_domain" in str(e.orig) or "domain" in str(e.orig).lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message": "El dominio ya está en uso.",
                        "code": "USER_DOMAIN_EXISTS",
                        "field": "domain"
                    }
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "Error al actualizar el usuario.",
                    "code": "USER_UPDATE_FAILED"
                }
            )
