from app.services.auth_service import (
    get_current_user,
    verify_password,
    create_access_token,
    get_user_by_email,
    get_user_by_username,
    hash_password
)
from app.models.user import User
from app.schemas.user import UserLogin, UserRegistration, UserResponse, TokenResponse

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(userdata: UserRegistration,
                   db: AsyncSession = Depends(get_db)):

    existing_email = await get_user_by_email(db, userdata.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    existing_username = await get_user_by_username(db, userdata.username) 
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    new_user = User(
        username=userdata.username,
        email=userdata.email,
        hashed_password=hash_password(userdata.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(userdata: UserLogin,
                db: AsyncSession = Depends(get_db)):

    user = await get_user_by_email(db, userdata.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(userdata.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_me(token: str,
                 db: AsyncSession = Depends(get_db)):

    user = await get_current_user(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return user