from aiogram import Router
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from bot.bl.game import get_finished_games_for_user
from bot.db.models import User
from bot.middlewares.i18n import gettext as _

router = Router()


@router.inline_query()
async def handle_inline_query(query: InlineQuery, user: User) -> None:
    results = []

    new_game_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=_('btn-accept-join'),
            callback_data="accept:new"
        )],
        [InlineKeyboardButton(
            text=_('btn-cancel'),
            callback_data="cancel:new"
        )]
    ])

    results.append(
        InlineQueryResultArticle(
            id="checkers_invite",
            title=_('inline-title'),
            description=_('inline-description'),
            input_message_content=InputTextMessageContent(
                message_text=_('inline-invitation-message'),
                parse_mode="HTML"
            ),
            reply_markup=new_game_keyboard,
            thumbnail_url=(
                "https://em-content.zobj.net/thumbs/120/"
                "apple/354/video-game_1f3ae.png"
            )
        )
    )

    finished_games = await get_finished_games_for_user(user.id, limit=10)

    for game in finished_games:
        opponent = (
            game.black_player
            if game.white_player_id == user.id
            else game.white_player
        )
        opponent_name = opponent.first_name if opponent else "Unknown"

        if game.winner_id is None:
            result_text = _('history-result-draw')
        elif game.winner_id == user.id:
            result_text = _('history-result-won')
        else:
            result_text = _('history-result-lost')

        date_str = (
            game.finished_at.strftime("%Y-%m-%d")
            if game.finished_at
            else "Unknown"
        )

        history_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=_('btn-view-history'),
                callback_data=f"hview:{game.id}"
            )]
        ])

        results.append(
            InlineQueryResultArticle(
                id=f"history_{game.id}",
                title=_('history-title', opponent=opponent_name),
                description=_(
                    'history-description',
                    result=result_text,
                    date=date_str
                ),
                input_message_content=InputTextMessageContent(
                    message_text=_(
                        'history-message',
                        opponent=opponent_name,
                        result=result_text,
                        date=date_str
                    ),
                    parse_mode="HTML"
                ),
                reply_markup=history_keyboard,
                thumbnail_url=(
                    "https://em-content.zobj.net/thumbs/120/"
                    "apple/354/trophy_1f3c6.png"
                )
            )
        )

    await query.answer(
        results=results,  # type: ignore[arg-type]
        is_personal=True,
        cache_time=1
    )
