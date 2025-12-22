from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.bl.user import get_user_stats
from bot.db.models import User

router = Router()


@router.message(Command("stats"))
async def handle_stats_command(message: Message, user: User) -> None:
    """Handle /stats command to show user statistics."""
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
    """Handle /start command."""
    text = (
        f"👋 Welcome to Checkers Bot, {user.first_name}!\n\n"
        f"To start a game:\n"
        f"1. Type @{message.bot.username} in any chat\n"
        f"2. Select 'Start Checkers Game'\n"
        f"3. Wait for someone to accept!\n\n"
        f"Commands:\n"
        f"/stats - View your statistics\n"
        f"/help - Show this help message"
    )

    await message.answer(text, parse_mode="HTML")


@router.message(Command("help"))
async def handle_help_command(message: Message) -> None:
    """Handle /help command."""
    text = (
        f"🎮 <b>How to Play Checkers</b>\n\n"
        f"<b>Starting a Game:</b>\n"
        f"• Use inline mode to send game invitation\n"
        f"• Wait for opponent to accept\n\n"
        f"<b>Playing:</b>\n"
        f"• Tap a piece to select it\n"
        f"• Tap a green circle to move there\n"
        f"• Captures are mandatory!\n"
        f"• Reach the opposite end to get a King\n\n"
        f"<b>Winning:</b>\n"
        f"• Capture all opponent pieces\n"
        f"• Block opponent from moving\n\n"
        f"<b>Commands:</b>\n"
        f"/stats - View your statistics\n"
        f"/help - Show this help"
    )

    await message.answer(text, parse_mode="HTML")
