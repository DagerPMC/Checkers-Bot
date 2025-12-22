from typing import Callable, Dict, Any, Awaitable
from time import time

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message


class ThrottlingMiddleware(BaseMiddleware):
    """Middleware to prevent flood attacks by throttling user requests."""

    def __init__(self, rate_limit: float = 0.5):
        """
        Initialize throttling middleware.

        Args:
            rate_limit: Minimum seconds between requests (default 0.5 = 2 requests/sec)
        """
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

        # Check last request time
        if user_id in self.user_timestamps:
            time_passed = current_time - self.user_timestamps[user_id]

            if time_passed < self.rate_limit:
                # Too many requests - silently ignore
                if isinstance(event, CallbackQuery):
                    await event.answer("Too many requests, please slow down", show_alert=False)
                return None

        # Update timestamp
        self.user_timestamps[user_id] = current_time

        # Clean old timestamps (keep only last 1000 users)
        if len(self.user_timestamps) > 1000:
            sorted_items = sorted(self.user_timestamps.items(), key=lambda x: x[1])
            self.user_timestamps = dict(sorted_items[-500:])

        return await handler(event, data)
