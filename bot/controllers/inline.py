from aiogram import Router
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from bot.middlewares.i18n import gettext as _

router = Router()


@router.inline_query()
async def handle_inline_query(query: InlineQuery) -> None:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=_('btn-accept-join'),
            callback_data="accept:new"
        )],
        [InlineKeyboardButton(
            text=_('btn-cancel'),
            callback_data="cancel:new"
        )]
    ])

    results = [
        InlineQueryResultArticle(
            id="checkers_invite",
            title=_('inline-title'),
            description=_('inline-description'),
            input_message_content=InputTextMessageContent(
                message_text=_('inline-invitation-message'),
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
