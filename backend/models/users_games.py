from sqlalchemy import (
    CheckConstraint,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base
from backend.users.enums import FriendRequestStatus

# User, Game, and UserGame share a file to avoid circular imports.


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nickname: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)

    user_games = relationship("UserGame", back_populates="user")
    sent_requests: Mapped[list["FriendRequest"]] = relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.requesting_user_id",
        back_populates="sender",
    )
    received_requests: Mapped[list["FriendRequest"]] = relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.requested_user_id",
        back_populates="receiver",
    )


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    user_games = relationship("UserGame", back_populates="game")


class UserGame(Base):
    __tablename__ = "users_games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    game_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("games.id"), nullable=False
    )

    user = relationship("User", back_populates="user_games")
    game = relationship("Game", back_populates="user_games")

    __table_args__ = (UniqueConstraint("user_id", "game_id", name="uq_user_game"),)


class FriendRequest(Base):
    __tablename__ = "friend_requests"
    __table_args__ = (
        CheckConstraint(
            "requesting_user_id != requested_user_id",
            name="check_users_are_different",
        ),
        UniqueConstraint(
            "requesting_user_id", "requested_user_id", name="uq_friend_request_users"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    requesting_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    requested_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )

    status: Mapped[FriendRequestStatus] = mapped_column(
        Enum(FriendRequestStatus), default=FriendRequestStatus.PENDING, nullable=False
    )

    sender: Mapped["User"] = relationship(
        "User",
        foreign_keys=[requesting_user_id],
        back_populates="sent_requests",
    )
    receiver: Mapped["User"] = relationship(
        "User",
        foreign_keys=[requested_user_id],
        back_populates="received_requests",
    )


Index(
    "uq_active_friend_request_users",
    func.least(FriendRequest.requesting_user_id, FriendRequest.requested_user_id),
    func.greatest(FriendRequest.requesting_user_id, FriendRequest.requested_user_id),
    unique=True,
    postgresql_where=FriendRequest.status.in_(
        [FriendRequestStatus.PENDING, FriendRequestStatus.ACCEPTED]
    ),
)
