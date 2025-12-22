from typing import Annotated
from uuid import UUID

from sqlalchemy import BIGINT, ForeignKey
from sqlalchemy.orm import mapped_column

str50 = Annotated[str, 50]

int_pk = Annotated[int, mapped_column(primary_key=True)]

uuid_pk = Annotated[UUID, mapped_column(primary_key=True)]

user_fk = Annotated[
    int, mapped_column(BIGINT, ForeignKey('users.id', ondelete='CASCADE'))
]

game_fk = Annotated[
    UUID, mapped_column(ForeignKey('games.id', ondelete='CASCADE'))
]
