from aiogram import Router

from bot.controllers.game import router as game_router
from bot.controllers.history import router as history_router
from bot.controllers.inline import router as inline_router
from bot.controllers.stats import router as stats_router

router = Router()
router.include_router(inline_router)
router.include_router(game_router)
router.include_router(history_router)
router.include_router(stats_router)
