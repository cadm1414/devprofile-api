from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.context.identity.api.schemas.user_schema import UserCreate, UserOut, UserUpdate, PasswordUpdate
from app.context.identity.application.usecases.register_user_use_case import RegisterUserUseCase
from app.context.identity.application.usecases.get_user_by_id_use_case import GetUserByIdUseCase
from app.context.identity.application.usecases.update_user_use_case import UpdateUserUseCase
from app.context.identity.application.usecases.delete_user_use_case import DeleteUserUseCase
from app.context.identity.application.usecases.update_password_use_case import UpdatePasswordUseCase
from app.context.identity.infrastructure.repositories.user_repository import UserRepository
from app.context.identity.domain.models.user_model import User
from app.common.dependencies import get_current_user

router = APIRouter(
    prefix="/identity",
    tags=["identity"]
)

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    use_case = RegisterUserUseCase(repo, db)
    user = use_case.execute(user_data)
    return user

@router.get("/me", response_model=UserOut, status_code=status.HTTP_200_OK)
def get_user_by_token(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):    
    repo = UserRepository(db)
    use_case = GetUserByIdUseCase(repo, db)
    user = use_case.execute(current_user.id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/me", response_model=UserOut, status_code=status.HTTP_200_OK)
def update_user_me(user_data: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = UserRepository(db)
    use_case = UpdateUserUseCase(repo, db)
    updated_user = use_case.execute(current_user.id, user_data)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_me(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = UserRepository(db)
    use_case = DeleteUserUseCase(repo, db)
    success = use_case.execute(user_id=current_user.id, requesting_user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para eliminar este usuario")
    return

@router.put("/me/password", status_code=status.HTTP_200_OK)
def update_my_password(
    password_data: PasswordUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):    
    repo = UserRepository(db)
    use_case = UpdatePasswordUseCase(repo, db)
    result = use_case.execute(current_user.id, password_data)
    return result



@router.get("/users/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def get_user(user_id: int, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    use_case = GetUserByIdUseCase(repo, db)
    user = use_case.execute(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    use_case = UpdateUserUseCase(repo, db)
    updated_user = use_case.execute(user_id, user_data)

    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return updated_user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = UserRepository(db)
    use_case = DeleteUserUseCase(repo, db)
    success = use_case.execute(user_id=user_id, requesting_user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para eliminar este usuario")
    
    return
