from typing import AsyncGenerator
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.repositories.users import UsersRepository
from app.usecases.auth import AuthUseCase
from app.core.security import decode_token
from app.core.exceptions import (
    InvalidTokenError,
    TokenExpiredError,
    UserNotFoundError,
)
from app.schemas.user import UserPublic


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_users_repo(
    session: AsyncSession = Depends(get_db),
) -> UsersRepository:
    return UsersRepository(session)


def get_auth_uc(
    repo: UsersRepository = Depends(get_users_repo),
) -> AuthUseCase:
    return AuthUseCase(repo)


def get_current_user_id(
    token: str = Depends(oauth2_scheme),
) -> int:
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise InvalidTokenError()

        return int(user_id)

    except TokenExpiredError:
        raise

    except Exception:
        raise InvalidTokenError()


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    repo: UsersRepository = Depends(get_users_repo),
) -> UserPublic:
    user = await repo.get_by_id(user_id)

    if not user:
        raise UserNotFoundError()

    return UserPublic.model_validate(user)