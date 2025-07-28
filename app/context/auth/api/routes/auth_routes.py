from fastapi import APIRouter, Depends, HTTPException, status
from app.context.auth.application.usecases.access_use_case import AccessUseCase
from app.context.identity.infrastructure.repositories.user_repository import UserRepository
from app.context.auth.api.schemas.auth_schema import LoginRequest, AccessResponse
from sqlalchemy.orm import Session
from app.config.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/access",response_model=AccessResponse, status_code=status.HTTP_200_OK)
async def access(request: LoginRequest, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    use_case = AccessUseCase(repo)
    
    token = await use_case.execute(request.email, request.password)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    return {"access_token": token, "token_type": "bearer"}
