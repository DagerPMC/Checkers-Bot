from aiogram import Router
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

router = Router()


@router.inline_query()
async def handle_inline_query(query: InlineQuery) -> None:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="✅ Accept & Join",
            callback_data="accept:new"
        )],
        [InlineKeyboardButton(
            text="❌ Cancel",
            callback_data="cancel:new"
        )]
    ])

    results = [
        InlineQueryResultArticle(
            id="checkers_invite",
            title="🎮 Start Checkers Game",
            description="Send a checkers game invitation to this chat",
            input_message_content=InputTextMessageContent(
                message_text=(
                    "🎮 <b>Checkers Game Invitation</b>\n\n"
                    "Tap 'Accept & Join' to start playing!"
                ),
                parse_mode="HTML"
            ),
            reply_markup=keyboard,
            thumbnail_url=(
                "https://em-content.zobj.net/thumbs/120/"
                "apple/354/video-game_1f3ae.png"
            )
        )
    ]

    await query.answer(
        results=results,  # type: ignore[arg-type]
        is_personal=True,
        cache_time=1
    )
