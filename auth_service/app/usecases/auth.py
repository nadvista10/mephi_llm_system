from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.core.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserNotFoundError,
)
from app.schemas.auth import RegisterRequest
from app.schemas.user import UserPublic
from app.repositories.users import UsersRepository


class AuthUseCase:
    def __init__(self, users_repo: UsersRepository):
        self.users_repo = users_repo


    async def register(self, data: RegisterRequest) -> UserPublic:
        existing_user = await self.users_repo.get_by_email(data.email)

        if existing_user:
            raise UserAlreadyExistsError()

        password_hash = hash_password(data.password)

        user = await self.users_repo.create(
            email=data.email,
            password_hash=password_hash,
            role="user",
        )

        return UserPublic.model_validate(user)


    async def login(self, email: str, password: str) -> str:
        user = await self.users_repo.get_by_email(email)

        if not user:
            raise InvalidCredentialsError()

        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        token = create_access_token(
            {
                "sub": str(user.id),
                "role": user.role,
            }
        )

        return token


    async def me(self, user_id: int) -> UserPublic:
        user = await self.users_repo.get_by_id(user_id)

        if not user:
            raise UserNotFoundError()

        return UserPublic.model_validate(user)