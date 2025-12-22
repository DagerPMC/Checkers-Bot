import typing as t
from datetime import datetime
from enum import StrEnum, auto
from uuid import UUID, uuid4

from sqlalchemy import JSON, BIGINT, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.db.base import Base
from bot.db.mixin import CreatedUpdatedAtMixin
from bot.db.types import user_fk, uuid_pk

if t.TYPE_CHECKING:
    from bot.db.models import User, Move


class GameStatus(StrEnum):
    PENDING = auto()
    ACTIVE = auto()
    FINISHED = auto()
    CANCELLED = auto()


class PlayerColor(StrEnum):
    WHITE = auto()
    BLACK = auto()


class Game(Base, CreatedUpdatedAtMixin):
    __tablename__ = 'games'

    id: Mapped[uuid_pk] = mapped_column(default=uuid4)

    # Players
    white_player_id: Mapped[user_fk]
    black_player_id: Mapped[user_fk | None]

    # Chat info
    chat_id: Mapped[int] = mapped_column(BIGINT)
    message_id: Mapped[int] = mapped_column(BIGINT)

    # Game state
    board_state: Mapped[dict] = mapped_column(JSON)
    current_turn: Mapped[PlayerColor] = mapped_column(
        Enum(PlayerColor), default=PlayerColor.WHITE
    )
    status: Mapped[GameStatus] = mapped_column(
        Enum(GameStatus), default=GameStatus.PENDING
    )

    # Result
    winner_id: Mapped[int | None] = mapped_column(BIGINT, nullable=True)
    finished_at: Mapped[datetime | None]

    # Relationships
    white_player: Mapped['User'] = relationship(
        foreign_keys='Game.white_player_id',
        back_populates='games_as_white'
    )
    black_player: Mapped['User | None'] = relationship(
        foreign_keys='Game.black_player_id',
        back_populates='games_as_black'
    )
    moves: Mapped[list['Move']] = relationship(back_populates='game')
