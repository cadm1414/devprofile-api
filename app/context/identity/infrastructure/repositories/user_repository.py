# app/context/identity/infrastructure/repositories/user_repository.py

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.context.identity.domain.models.user_model import User
from passlib.context import CryptContext
from app.context.identity.domain.repositories.user_repository_interface import IUserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository(IUserRepository):

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = self.db.execute(stmt).scalar_one_or_none()
        return result

    def create_user(self, email: str, name: str, last_name: str, full_name: str, password: str) -> User:
        hashed_password = pwd_context.hash(password)
        user = User(
            email=email,
            name=name,
            last_name=last_name,   
            full_name=full_name,
            hashed_password=hashed_password
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)
    
    def update(self, user: User, user_data: dict) -> User:
        for key, value in user_data.items():
            setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user: User)-> bool:
        self.db.delete(user)
        self.db.commit()
        return True
