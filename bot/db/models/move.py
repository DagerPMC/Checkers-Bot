import typing as t

from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.db.base import Base
from bot.db.mixin import CreatedAtMixin
from bot.db.types import game_fk, int_pk, user_fk

if t.TYPE_CHECKING:
    from bot.db.models import Game, User


class Move(Base, CreatedAtMixin):
    __tablename__ = 'moves'

    id: Mapped[int_pk]
    game_id: Mapped[game_fk]
    player_id: Mapped[user_fk]

    from_position: Mapped[str]
    to_position: Mapped[str]
    captured_positions: Mapped[list | None] = mapped_column(JSON, nullable=True)
    promoted: Mapped[bool] = mapped_column(default=False)
    move_number: Mapped[int]

    # Relationships
    game: Mapped['Game'] = relationship(back_populates='moves')
