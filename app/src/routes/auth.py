# from typing import List
from src.services.email import send_email
from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
# from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import users as repository_users
from src.services.auth import auth_service

from src.schemas.schemas import UserResponse, UserSchema, TokenModel
from src.schemas.schemas import RequestEmail
from src.exceptions.exceptions import RETURN_MSG
from src.entity.models import User

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=RETURN_MSG.user_exists)
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)

    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    # token_verification = auth_service.create_email_token(
    #     {"sub": new_user.email})
    # print(f"{request.base_url}api/auth/confirmed_email/{token_verification}")

    return {"user": new_user, "detail": RETURN_MSG.user_created}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=RETURN_MSG.verification_error)
    if user.confirmed:
        return {"message": RETURN_MSG.email_already_confirmed}
    await repository_users.confirmed_email(email, db)
    return {"message": RETURN_MSG.email_confirmed}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.email, db)
    
    if not user:
        return {"message": RETURN_MSG.email_invalid}
    if user.confirmed:
        return {"message": RETURN_MSG.email_already_confirmed}
    
    background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": RETURN_MSG.emaii_check_confirmation}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=RETURN_MSG.email_invalid)
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=RETURN_MSG.email_not_confirmed)
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=RETURN_MSG.password_invalid)
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    db.add(user)
    db.commit()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=RETURN_MSG.verification_error)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=RETURN_MSG.token_refresh_invalid)

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    
    try:
        token = credentials.credentials
        user.refresh_token = None
        db.commit()
        expired = await auth_service.get_exp_from_token(token)
        return {"logout": RETURN_MSG.user_logout}
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=RETURN_MSG.user_logout)
