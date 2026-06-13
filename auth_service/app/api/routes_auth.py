from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserPublic
from app.usecases.auth import AuthUseCase
from app.api.deps import get_auth_uc, get_current_user


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserPublic)
async def register(
    data: RegisterRequest,
    uc: AuthUseCase = Depends(get_auth_uc),
):
    return await uc.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    uc: AuthUseCase = Depends(get_auth_uc),
):
    token = await uc.login(
        email=form.username,
        password=form.password,
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
    )


@router.get("/me", response_model=UserPublic)
async def me(
    user: UserPublic = Depends(get_current_user),
):
    return user