from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.bl.user import get_user_stats
from bot.db.models import User
from bot.middlewares.i18n import gettext as _

router = Router()


@router.message(Command("stats"))
async def handle_stats_command(message: Message, user: User) -> None:
    stats = await get_user_stats(user.id)

    text = (
        f"{_('stats-header')}\n\n"
        f"{_('stats-total-games', count=stats['total_games'])}\n"
        f"{_('stats-wins', count=stats['wins'])}\n"
        f"{_('stats-losses', count=stats['losses'])}\n"
        f"{_('stats-win-rate', rate=f'{stats['win_rate']:.1f}')}"
    )

    await message.answer(text, parse_mode="HTML")


@router.message(Command("start"))
async def handle_start_command(message: Message, user: User) -> None:
    bot_username = (
        message.bot.username  # type: ignore[attr-defined]
        if message.bot and message.bot.username  # type: ignore[attr-defined]
        else "checkersbot"
    )
    text = _(
        'start-message',
        user_name=user.first_name,
        bot_username=bot_username
    )

    await message.answer(text, parse_mode="HTML")


@router.message(Command("help"))
async def handle_help_command(message: Message) -> None:
    text = _('help-message')

    await message.answer(text, parse_mode="HTML")
