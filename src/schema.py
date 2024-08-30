from pydantic import BaseModel, EmailStr
from typing import Optional

class GetUser(BaseModel):
    id : int
    email: EmailStr
    username : Optional[str]
    is_active : bool

    class Config:
        form_attributes = True

class LoginUser(BaseModel):
    email: EmailStr
    password: str

    class Config:
        form_attributes = True

class PostUser(BaseModel):
    email: EmailStr
    username: Optional[str]
    password: str

    class Config:
        form_attributes = True

class ChangePassword(BaseModel):
    old_password : str
    new_password : str
    confirm_password : str



class EmailSchema(BaseModel):
    email: EmailStr

class ResetPasswordSchema(BaseModel):
    new_password : str
    confirm_password: str