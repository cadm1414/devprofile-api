from app.context.identity.domain.repositories.user_repository_interface import IUserRepository
from sqlalchemy.orm import Session

class DeleteUserUseCase:
    def __init__(self, user_repo: IUserRepository, db: Session):
        self.user_repo = user_repo
        self.db = db

    def execute(self, user_id: int, requesting_user_id: int) -> bool:
        
        if user_id != requesting_user_id:
            return False

        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False
        
        self.user_repo.delete(user)
        
        return True