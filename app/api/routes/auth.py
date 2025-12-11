from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead)
async def register(
    data: UserCreate,
    user_service: UserService = Depends(),
):
    return await user_service.register(data)


@router.post("/login", response_model=Token)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(),
):
    access_token, refresh_token = await user_service.authenticate_and_create_tokens(
        email=form_data.username,
        password=form_data.password,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
        path="/",
    )

    return Token(access_token=access_token)


@router.post("/refresh", response_model=Token)
async def refresh(
    request: Request,
    response: Response,
    user_service: UserService = Depends(),
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token",
        )

    new_access, new_refresh = await user_service.refresh_tokens(refresh_token)

    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
        path="/",
    )

    return Token(access_token=new_access)


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="refresh_token",
        path="/",
        samesite="lax",
        secure=False,
        httponly=True,
    )
    return {"detail": "Logged out successfully"}
