import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
)
from aiohttp import web

from bot.config import Config, UpdateStrategy
from bot.controllers.router import router
from bot.db.session import init_session
from bot.middlewares.i18n import setup_i18n
from bot.middlewares.session import session_middleware
from bot.middlewares.throttling import ThrottlingMiddleware
from bot.middlewares.user import user_middleware
from bot.utils.setup import init_config

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = web.Application()


async def on_startup(dispatcher: Dispatcher, bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=False)
    if (
        Config.c.updates_strategy is UpdateStrategy.webhook
        and Config.c.host_url
    ):
        await bot.set_webhook(
            f'https://{Config.c.host_url}/webhook/main'
        )


def main() -> None:
    session = AiohttpSession()
    bot = Bot(
        token=Config.c.token,
        session=session,
        default=DefaultBotProperties(parse_mode='HTML')
    )

    dp = Dispatcher()
    dp.startup.register(on_startup)
    dp.update.outer_middleware(session_middleware)

    i18n, i18n_middleware = setup_i18n()
    i18n_middleware.setup(dp)

    dp.update.outer_middleware(user_middleware)
    dp.update.outer_middleware(ThrottlingMiddleware(rate_limit=0.3))

    dp.include_router(router)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    if Config.c.updates_strategy is UpdateStrategy.webhook:
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(
            app, path='/webhook/main'
        )
        setup_application(app, dp, bot=bot)
        web.run_app(app, host='0.0.0.0', port=8080)
    elif Config.c.updates_strategy is UpdateStrategy.polling:
        asyncio.run(dp.start_polling(bot))


if __name__ == '__main__':
    init_config()
    init_session()
    main()
