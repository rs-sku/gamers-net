import re
from typing import Literal

from pydantic import BaseModel, field_validator, model_validator

from backend.users.enums import FriendRequestStatus


def validate_not_empty(value: str) -> str:
    if not value.strip():
        raise ValueError("Field must not be empty")
    return value


class UserRequestSchema(BaseModel):
    nickname: str
    email: str
    password: str

    @field_validator("password")
    def validate_password(cls, password: str) -> str:
        validate_not_empty(password)
        if len(password) < 8:
            raise ValueError(
                "Password must be at least 8 characters long, contains at least one uppercase "
                "letter, one lowercase letter, one digit and one special character"
            )
        if not re.search(r"[A-Z]", password):
            raise ValueError(
                "Password must be at least 8 characters long, contains at least one uppercase "
                "letter, one lowercase letter, one digit and one special character"
            )
        if not re.search(r"[a-z]", password):
            raise ValueError(
                "Password must be at least 8 characters long, contains at least one uppercase "
                "letter, one lowercase letter, one digit and one special character"
            )
        if not re.search(r"[0-9]", password):
            raise ValueError(
                "Password must be at least 8 characters long, contains at least one uppercase "
                "letter, one lowercase letter, one digit and one special character"
            )
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError(
                "Password must be at least 8 characters long, contains at least one uppercase "
                "letter, one lowercase letter, one digit and one special character"
            )
        return password

    @field_validator("nickname")
    def validate_nickname(cls, nickname: str) -> str:
        validate_not_empty(nickname)
        if len(nickname) < 3 or len(nickname) > 20:
            raise ValueError("Nickname must be between 3 and 20 characters")
        return nickname

    @field_validator("email")
    def validate_email(cls, email: str) -> str:
        validate_not_empty(email)
        if len(email) < 3 or len(email) > 20:
            raise ValueError("Email must be between 3 and 20 characters")
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            raise ValueError("Please enter a valid email address")
        return email


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
