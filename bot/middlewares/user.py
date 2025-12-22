import typing as t

from aiogram.types import TelegramObject

from bot.bl.user import create_or_update_user


async def user_middleware(
    handler: t.Callable[[
        TelegramObject, dict[str, t.Any]], t.Awaitable[t.Any]
    ],
    event: TelegramObject,
    data: dict[str, t.Any]
) -> None:
    tg_user = data.get('event_from_user')
    if tg_user:
        user = await create_or_update_user(
            id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name
        )
        data['user'] = user
    await handler(event, data)
