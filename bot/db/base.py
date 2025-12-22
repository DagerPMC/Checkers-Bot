from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase

from bot.db.types import str50


class Base(DeclarativeBase):
    type_annotation_map = {
        str50: String(50)
    }
