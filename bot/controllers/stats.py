from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.bl.user import get_user_stats
from bot.db.models import User

router = Router()


@router.message(Command("stats"))
async def handle_stats_command(message: Message, user: User) -> None:
    stats = await get_user_stats(user.id)

    text = (
        f"📊 <b>Your Checkers Statistics</b>\n\n"
        f"🎮 Total Games: {stats['total_games']}\n"
        f"🏆 Wins: {stats['wins']}\n"
        f"💔 Losses: {stats['losses']}\n"
        f"📈 Win Rate: {stats['win_rate']:.1f}%"
    )

    await message.answer(text, parse_mode="HTML")


@router.message(Command("start"))
async def handle_start_command(message: Message, user: User) -> None:
    bot_username = (
        message.bot.username  # type: ignore[attr-defined]
        if message.bot and message.bot.username  # type: ignore[attr-defined]
        else "checkersbot"
    )
    text = (
        f"👋 Welcome to Checkers Bot, {user.first_name}!\n\n"
        f"To start a game:\n"
        f"1. Type @{bot_username} in any chat\n"
        f"2. Select 'Start Checkers Game'\n"
        f"3. Wait for someone to accept!\n\n"
        f"Commands:\n"
        f"/stats - View your statistics\n"
        f"/help - Show this help message"
    )

    await message.answer(text, parse_mode="HTML")


@router.message(Command("help"))
async def handle_help_command(message: Message) -> None:
    text = (
        "🎮 <b>How to Play Checkers</b>\n\n"
        "<b>Starting a Game:</b>\n"
        "• Use inline mode to send game invitation\n"
        "• Wait for opponent to accept\n\n"
        "<b>Playing:</b>\n"
        "• Tap a piece to select it\n"
        "• Tap a green circle to move there\n"
        "• Captures are mandatory!\n"
        "• Reach the opposite end to get a King\n\n"
        "<b>Winning:</b>\n"
        "• Capture all opponent pieces\n"
        "• Block opponent from moving\n\n"
        "<b>Commands:</b>\n"
        "/stats - View your statistics\n"
        "/help - Show this help"
    )

    await message.answer(text, parse_mode="HTML")
