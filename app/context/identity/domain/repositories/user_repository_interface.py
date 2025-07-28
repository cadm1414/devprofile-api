from abc import ABC, abstractmethod
from app.context.identity.domain.models.user_model import User

class IUserRepository(ABC):

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        pass  
    