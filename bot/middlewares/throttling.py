from time import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 0.5):
        self.rate_limit = rate_limit
        self.user_timestamps: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")

        if not user:
            return await handler(event, data)

        user_id = user.id
        current_time = time()

        if user_id in self.user_timestamps:
            time_passed = current_time - self.user_timestamps[user_id]

            if time_passed < self.rate_limit:
                if isinstance(event, CallbackQuery):
                    await event.answer(
                        "Too many requests, please slow down",
                        show_alert=False
                    )
                return None

        self.user_timestamps[user_id] = current_time

        if len(self.user_timestamps) > 1000:
            sorted_items = sorted(
                self.user_timestamps.items(), key=lambda x: x[1]
            )
            self.user_timestamps = dict(sorted_items[-500:])

        return await handler(event, data)
