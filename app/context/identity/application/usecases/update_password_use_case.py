from sqlalchemy.orm import Session
from app.context.identity.domain.repositories.user_repository_interface import IUserRepository
from app.context.identity.api.schemas.user_schema import PasswordUpdate
from passlib.context import CryptContext
from fastapi import HTTPException, status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UpdatePasswordUseCase:
    def __init__(self, repository: IUserRepository, db: Session):
        self.repository = repository
        self.db = db

    def execute(self, user_id: int, password_data: PasswordUpdate):        
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Usuario no encontrado"
            )
        
        if not pwd_context.verify(password_data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="La contraseña actual es incorrecta"
            )
        
        if pwd_context.verify(password_data.new_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="La nueva contraseña debe ser diferente a la actual"
            )
        
        hashed_new_password = pwd_context.hash(password_data.new_password)
                
        updated_data = {"hashed_password": hashed_new_password}
        self.repository.update(user, updated_data)

        return {"message": "Contraseña actualizada exitosamente"}
