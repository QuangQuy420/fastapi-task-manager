from jose import ExpiredSignatureError, JWTError
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import create_refresh_token, decode_refresh_token, get_password_hash, verify_password, create_access_token
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def register(self, data: UserCreate):
        existing = self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        hashed = get_password_hash(data.password)
        try:
            return self.repo.create(
                email=data.email,
                full_name=data.full_name,
                hashed_password=hashed,
            )
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    def authenticate_and_create_tokens(self, email: str, password: str) -> tuple[str, str]:
        user = self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email or password",
            )

        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        return access_token, refresh_token


    def refresh_tokens(self, refresh_token: str) -> tuple[str, str]:
        """
        Validate refresh token, then issue new access + refresh token.
        (Stateless rotation: we don't store tokens in DB yet.)
        """
        try:
            user_id = decode_refresh_token(refresh_token)
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired",
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        # Check user still exists / active:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        # Rotate: new access + new refresh
        new_access = create_access_token(subject=user.id)
        new_refresh = create_refresh_token(subject=user.id)

        return new_access, new_refresh