from passlib.context import CryptContext
from typing import Optional
from datetime import datetime, timedelta
from app.config import settings
from jose import JWTError, jwt
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

pwd_context = CryptContext(
    schemes = ["bcrypt"],
    deprecated = "auto"
)

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode =  data.copy()
    expire =  datetime.utcnow() + (expires_delta or timedelta(minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update(
        {"exp": expire}
        )
    return jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm = settings.ALGORITHM
        )

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()

async def get_user_by_username(db:AsyncSession,username: str):
    result = await db.execute(
        select(User).where(User.username == username)
    )
    return result.scalar_one_or_none()

async def get_current_user(token: str, db: AsyncSession) -> Optional[User]:
    try:
        payload  = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms = [settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()