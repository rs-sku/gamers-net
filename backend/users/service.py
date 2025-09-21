from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from backend.users.repository import Repository
from backend.users.schemas import UserLoginSchema, UserRequestSchema, UserResponseSchema
from backend.users.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)


class Service:
    def __init__(self, repository: Repository):
        self._repository = repository

    async def add_user(self, data: UserRequestSchema) -> UserResponseSchema:
        validated_data = data.model_dump()
        validated_data["password"] = get_password_hash(validated_data["password"])
        try:
            user = await self._repository.add_user(validated_data)
            return UserResponseSchema.model_validate(user, from_attributes=True)
        except IntegrityError as e:
            if "users_nickname_key" in str(e.orig):
                raise HTTPException(status_code=409, detail="Nickname already exists")
            elif "users_email_key" in str(e.orig):
                raise HTTPException(status_code=409, detail="Email already exists")
            else:
                raise HTTPException(
                    status_code=409, detail="An unknown integrity error occurred"
                )

    async def get_users(self) -> list[UserResponseSchema]:
        users = await self._repository.get_users()
        return [
            UserResponseSchema.model_validate(user, from_attributes=True)
            for user in users
        ]

    async def authenticate_user(
        self, password: str, nickname: str | None = None, email: str | None = None
    ) -> int:
        user = None
        if nickname:
            user = await self._repository.get_user_by_filters(nickname=nickname)
        elif email:
            user = await self._repository.get_user_by_filters(email=email)
        if user is None:
            raise HTTPException(status_code=404, detail="User does not exist")
        if not verify_password(password, user.password):
            raise HTTPException(status_code=400, detail="Wrong password")
        return user.id

    async def login_user(self, data: UserLoginSchema) -> str:
        user_id = await self.authenticate_user(data.password, data.nickname, data.email)
        return create_access_token(data={"user_id": user_id})
