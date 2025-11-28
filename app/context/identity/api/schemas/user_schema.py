from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    last_name: str
    full_name: str
    password:str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    domain: Optional[str] = Field(None, max_length=50, pattern=r'^[a-zA-Z0-9]+$', description="Unique domain for public profile URL (alphanumeric only, no spaces or special characters)")

class PasswordUpdate(BaseModel):
    current_password: str = Field(..., min_length=6, description="Contraseña actual")
    new_password: str = Field(..., min_length=6, description="Nueva contraseña")
    confirm_password: str = Field(..., min_length=6, description="Confirmar nueva contraseña")
    
    @field_validator('confirm_password')
    def passwords_match(cls, v, info):
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Las contraseñas no coinciden')
        return v

class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str
    last_name: str
    full_name: str
    domain: Optional[str] = None

    class Config:
        orm_mode = True

