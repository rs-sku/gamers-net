import re
from typing import Literal

from pydantic import BaseModel, field_validator, model_validator

from backend.users.enums import FriendRequestStatus


class UserRequestSchema(BaseModel):
    nickname: str
    email: str
    password: str

    @field_validator("password")
    def validate_password(cls, password: str) -> str:
        if len(password) < 8:
            raise ValueError(
                "Password must be at least 8 characters long, contains at least one uppercase letter, "
                "one lowercase letter, one digit and one special character"
            )
        if not re.search(r"[A-Z]", password):
            raise ValueError(
                "Password must be at least 8 characters long, contains at least one uppercase letter, "
                "one lowercase letter, one digit and one special character"
            )
        if not re.search(r"[a-z]", password):
            raise ValueError(
                "Password must be at least 8 characters long, contains at least one uppercase letter, "
                "one lowercase letter, one digit and one special character"
            )
        if not re.search(r"[0-9]", password):
            raise ValueError(
                "Password must be at least 8 characters long, contains at least one uppercase letter, "
                "one lowercase letter, one digit and one special character"
            )
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError(
                "Password must be at least 8 characters long, contains at least one uppercase letter, "
                "one lowercase letter, one digit and one special character"
            )
        return password


class UserResponseSchema(BaseModel):
    id: int
    nickname: str
    email: str


class UserLoginSchema(BaseModel):
    email: str | None = None
    nickname: str | None = None
    password: str

    @model_validator(mode="after")
    def check_fields(self) -> "UserLoginSchema":
        if not self.email and not self.nickname:
            raise ValueError("Either email or nickname must be provided")
        if not self.password:
            raise ValueError("Password must not be empty")
        return self


class GetFriendsResponseSchema(BaseModel):
    friends: list[str]


class UpdatePendingFriendRequestStatusSchema(BaseModel):
    new_status: Literal[FriendRequestStatus.ACCEPTED, FriendRequestStatus.REJECTED]


class FriendRequestResponseSchema(BaseModel):
    id: int
    requesting_user_id: int
    requested_user_id: int
    status: FriendRequestStatus
