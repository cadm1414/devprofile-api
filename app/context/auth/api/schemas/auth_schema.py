from pydantic import BaseModel
class LoginRequest(BaseModel):
    email: str
    password: str

class AccessResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
    class Config:
        orm_mode = True
        