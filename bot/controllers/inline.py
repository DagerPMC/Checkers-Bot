from aiogram import Router
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

router = Router()


@router.inline_query()
async def handle_inline_query(query: InlineQuery) -> None:
    """Handle inline queries for game invitations."""
    # Create keyboard for invitation
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Accept & Join", callback_data="accept:new")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel:new")]
    ])

    results = [
        InlineQueryResultArticle(
            id="checkers_invite",
            title="🎮 Start Checkers Game",
            description="Send a checkers game invitation to this chat",
            input_message_content=InputTextMessageContent(
                message_text="🎮 <b>Checkers Game Invitation</b>\n\nTap 'Accept & Join' to start playing!",
                parse_mode="HTML"
            ),
            reply_markup=keyboard,
            thumbnail_url="https://em-content.zobj.net/thumbs/120/apple/354/video-game_1f3ae.png"
        )
    ]

    await query.answer(
        results=results,
        is_personal=True,
        cache_time=1
    )
