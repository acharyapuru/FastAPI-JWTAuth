from sqlalchemy.orm import Session
from pydantic import EmailStr
from fastapi import Depends, HTTPException, Request , status
from typing import Any, Optional, Union
from datetime import datetime, date, time, timedelta
import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.models import User
from src.schema import PostUser
from src.config import setting
from .password import get_hashed_password
from src.database import get_db


def get_user(db: Session, email: EmailStr):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: PostUser):
    hashed_password = get_hashed_password(user.password)
    db_user = User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_access_token(subject: Union[str, Any], expires_delta: int|None = None)-> str:
    if expires_delta is not None:
        expires_delta = datetime.now() + expires_delta
    else:
        expires_delta = datetime.now() + timedelta(minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expires_delta, "sub": str(subject)} 
    encoded_jwt = jwt.encode(to_encode, setting.secret_key, setting.algorithm)
    return encoded_jwt

def create_refresh_token(subject: Union[str,Any], expires_delta: int|None = None)-> str:
    if expires_delta is not None:
        expires_delta = datetime.now() + expires_delta
    else:
        expires_delta= datetime.now() + timedelta(minutes=setting.REFRESH_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, setting.secret_key, setting.algorithm)
    return encoded_jwt

def create_reset_token(user_id: int):
    payload = {
        "sub": str(user_id),
        "exp": datetime.now() + timedelta(hours=24)
    }
    return jwt.encode(payload, setting.secret_key, setting.algorithm)

def verify_reset_token(token:str):
    try:
        payload = jwt.decode(token, setting.secret_key, setting.algorithm)
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token Expired"
        )
    
    except jwt.InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )
    

def decodeJWT(jwttoken: str):
    try:
        payload = jwt.decode(jwttoken, setting.secret_key, setting.algorithm)
        return payload
    except jwt.InvalidTokenError:
        return None
    


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request:Request)-> Optional[str]:
        credentials : HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication scheme.")
            
            token = credentials.credentials
            if not self.verify_jwt(token):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token or expired token.")
            return token
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Authorization code.")
    
    def verify_jwt(self, jwttoken: str):
        try:
            payload = decodeJWT(jwttoken)
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.PyJWTError:
            return False
        
#jwt_bearer = JWTBearer()


#For protecting routes
def get_user_by_id(use_id:int, db: Session):
    return db.query(User).filter(User.id == use_id).first()

def get_current_user(token: str = Depends(JWTBearer()), db:Session =Depends(get_db))->User:
    payload = decodeJWT(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or expired token",
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or expired token",
        )
    
    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
