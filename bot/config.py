import typing as t
from enum import StrEnum, auto

from pydantic import BaseModel


class UpdateStrategy(StrEnum):
    polling = auto()
    webhook = auto()


class Settings(BaseModel):
    token: str
    updates_strategy: UpdateStrategy
    database_dns: str
    host_url: str | None = None  # Required for webhook mode


class Config(BaseModel):
    c: t.ClassVar[Settings]
