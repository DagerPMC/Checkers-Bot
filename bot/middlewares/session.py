import typing as t

from aiogram.types import TelegramObject

from bot.db.session import s


async def session_middleware(
    handler: t.Callable[[
        TelegramObject, dict[str, t.Any]], t.Awaitable[t.Any]
    ],
    event: TelegramObject,
    data: dict[str, t.Any]
) -> None:
    s.session = s.maker()
    try:
        await handler(event, data)
        await s.session.commit()
    finally:
        await s.session.close()
    return None
