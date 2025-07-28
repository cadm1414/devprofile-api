from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.context.identity.infrastructure.repositories.user_repository import UserRepository
from app.context.identity.domain.models.user_model import User

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
