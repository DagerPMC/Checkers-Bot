from time import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.methods import AnswerCallbackQuery
from aiogram.types import TelegramObject, Update


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 0.3):
        self.rate_limit = rate_limit
        self.user_timestamps: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        assert isinstance(event, Update)
        user = data.get("event_from_user")

        if not user:
            return await handler(event, data)

        user_id = user.id
        current_time = time()

        if user_id in self.user_timestamps:
            time_passed = current_time - self.user_timestamps[user_id]

            if time_passed < self.rate_limit:
                if event.callback_query is not None:
                    await AnswerCallbackQuery(
                        callback_query_id=event.callback_query.id,
                        text='Too many requests. Slow down',
                    ).as_(data.get('bot'))
                return None

        self.user_timestamps[user_id] = current_time

        if len(self.user_timestamps) > 1000:
            sorted_items = sorted(
                self.user_timestamps.items(), key=lambda x: x[1]
            )
            self.user_timestamps = dict(sorted_items[-500:])

        return await handler(event, data)
