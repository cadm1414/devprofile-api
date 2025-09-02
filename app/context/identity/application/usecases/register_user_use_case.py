from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.context.identity.domain.repositories.user_repository_interface import IUserRepository
from app.context.identity.api.schemas.user_schema import UserCreate
from app.context.identity.domain.models.user_model import User
from sqlalchemy.orm import Session

class RegisterUserUseCase:
    def __init__(self, user_repo: IUserRepository, db: Session):
        
        self.user_repo = user_repo
        self.db = db

    def execute(self, user_data: UserCreate) -> User:
        try:
            user = self.user_repo.create_user(
                email=user_data.email,
                name=user_data.name,
                last_name=user_data.last_name,
                full_name=user_data.full_name,
                password=user_data.password
            )            
            return user
        except IntegrityError as e:
            self.db.rollback()
            if "ix_users_email" in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message": "El correo ya está registrado.",
                        "code": "USER_EMAIL_EXISTS",
                        "field": "email"
                    }
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "Error al registrar el usuario.",
                    "code": "USER_REGISTRATION_FAILED"
                }
            )
