from contextvars import ContextVar

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncSessionTransaction,
    async_sessionmaker,
    create_async_engine,
)

from bot.config import Config

_session = ContextVar[AsyncSession]('session',)
_session_transaction = ContextVar[AsyncSessionTransaction | None](
    '_session_transaction', default=None
)


class _Session:
    maker: async_sessionmaker = None  # type: ignore[assignment]

    @property
    def session(self) -> AsyncSession:
        return _session.get()

    @session.setter
    def session(self, value: AsyncSession) -> None:
        _session.set(value)

    @property
    def session_transaction(self) -> AsyncSessionTransaction | None:
        return _session_transaction.get()

    @session_transaction.setter
    def session_transaction(self, value: AsyncSessionTransaction) -> None:
        _session_transaction.set(value)


s = _Session()


def init_session() -> None:
    eng = create_async_engine(
        Config.c.database_dns,
        echo=False,
        isolation_level='AUTOCOMMIT'
    )
    _Session.maker = async_sessionmaker(eng)
