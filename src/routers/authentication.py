from fastapi import FastAPI, Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from src.utils.password import verify_password
from src.utils.auth import create_access_token, create_refresh_token, create_user, get_user, create_reset_token, verify_reset_token
from src.database import get_db
from src.schema import GetUser, LoginUser, PostUser, ChangePassword, ResetPasswordSchema
from datetime import  timedelta
from fastapi.security import OAuth2PasswordBearer
from src.models import User
from src.utils.auth import get_current_user
from src.utils.password import verify_password, get_hashed_password
from src.utils.email import send_email
from starlette.background import BackgroundTasks

route = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2bearer = OAuth2PasswordBearer(
    tokenUrl="auth/login"
)

@route.post("/register", response_model=GetUser)
def register_user(payload: PostUser, db: Session = Depends(get_db)):
    if not payload.email:
        raise HTTPException(
            status=status.HTTP_403_FORBIDDEN,
            detail="Please provide an email address"
        )
    
    user = get_user(db, payload.email)
    if user:
        raise HTTPException(
            status=status.HTTP_403_FORBIDDEN,
            detail=f"User with email {payload.email} already exists"
        )
    
    user = create_user(db, payload)
    print(user)
    return user

@route.post("/login")
def login_user(payload: LoginUser, db:Session = Depends(get_db)):
    if not payload.email:
        raise HTTPException(
            status=status.HTTP_403_FORBIDDEN,
            detail="Please provide email address"
        )
    
    user = get_user(db, payload.email)
    hashed_password = user.hashed_password
    
    if not verify_password(payload.password, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    token = create_access_token(user.id, timedelta(minutes=30))
    refresh = create_refresh_token(user.id, timedelta(minutes=1008))

    return {
        "token_type": "bearer",
        "access_token": token,
        "refresh_token": refresh,
        "user_id": user.id
    }



@route.get("/users/me", response_model=GetUser)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user details
    """
    return current_user

@route.post("/change-password")
def change_password(change_password_data: ChangePassword, db:Session = Depends(get_db), request_user: User = Depends(get_current_user)):
    if not verify_password(change_password_data.old_password, request_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect",
        )
    
    if change_password_data.new_password != change_password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirm password didn't match",
        )
    
    hashed_password = get_hashed_password(change_password_data.new_password)
    request_user.hashed_password = hashed_password
    db.add(request_user)
    db.commit()
    return {"message": "Password updated successfully"}

@route.post("/forgot-password")
async def forgot_password(email: str, background_tasks: BackgroundTasks, db:Session = Depends(get_db)):
    user = db.query(User).filter(User.email==email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    reset_token = create_reset_token(user.id)
    background_tasks.add_task(send_email, user.email, reset_token)

    return {"message": "Reset link has been sent to your email"}

@route.post("/reset-password/{token}")
def reset_password(token: str, reset_password_data: ResetPasswordSchema, db:Session = Depends(get_db)):
    user_id = verify_reset_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    if reset_password_data.new_password != reset_password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirm password didn't match",
        )
    
    user = db.query(User).filter(User.id==user_id).first()
    hashed_password = get_hashed_password(reset_password_data.new_password)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()

    return {'success': True, 'status_code': status.HTTP_200_OK,
                 'message': 'Password Rest Successfull!'}