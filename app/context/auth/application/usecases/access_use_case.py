from fastapi import HTTPException, status
from app.context.auth.domain.services.password_service import verify_password
from app.context.auth.domain.services.jwt_generator_service import generate_jwt
from app.context.identity.domain.repositories.user_repository_interface import IUserRepository
class AccessUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def execute(self, email: str, password: str) -> str:
        user = self.user_repository.get_by_email(email)
        
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo. Contacte al administrador."
            )
        
        return generate_jwt(user.id, user.name, user.email)