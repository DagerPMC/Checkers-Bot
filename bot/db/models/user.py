import typing as t

from sqlalchemy import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.db.base import Base
from bot.db.mixin import CreatedAtMixin
from bot.db.types import int_pk

if t.TYPE_CHECKING:
    from bot.db.models import Game


class User(Base, CreatedAtMixin):
    __tablename__ = 'users'

    id: Mapped[int_pk] = mapped_column(BIGINT)
    username: Mapped[str | None]
    first_name: Mapped[str]
    last_name: Mapped[str | None]

    # Statistics
    total_games: Mapped[int] = mapped_column(default=0)
    wins: Mapped[int] = mapped_column(default=0)
    losses: Mapped[int] = mapped_column(default=0)

    # Relationships
    games_as_white: Mapped[list['Game']] = relationship(
        foreign_keys='Game.white_player_id',
        back_populates='white_player',
        overlaps='games_as_black'
    )
    games_as_black: Mapped[list['Game']] = relationship(
        foreign_keys='Game.black_player_id',
        back_populates='black_player',
        overlaps='games_as_white'
    )
