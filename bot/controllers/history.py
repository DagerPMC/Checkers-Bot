from functools import partial
from uuid import UUID

from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.bl.game import get_game_with_moves
from bot.bl.history import reconstruct_board_at_move
from bot.db.models import User
from bot.middlewares.i18n import gettext as _
from bot.middlewares.i18n import gettext_with_locale
from bot.utils.keyboard import create_history_board_keyboard

router = Router()


async def _edit_history_message(
    callback: CallbackQuery,
    text: str,
    keyboard=None
) -> None:
    if callback.message and hasattr(callback.message, 'edit_text'):
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    elif callback.inline_message_id and callback.bot:
        await callback.bot.edit_message_text(
            text=text,
            inline_message_id=callback.inline_message_id,
            parse_mode="HTML",
            reply_markup=keyboard
        )


@router.callback_query(F.data.startswith("hview:"))
async def handle_view_history(
    callback: CallbackQuery, user: User
) -> None:
    if not callback.data:
        await callback.answer(_('notif-invalid-request'))
        return

    game_id_str = callback.data.split(":")[1]

    try:
        game_id = UUID(game_id_str)
    except ValueError:
        await callback.answer(_('notif-invalid-game-id'))
        return

    game = await get_game_with_moves(game_id)
    if not game:
        await callback.answer(_('notif-game-not-found'))
        return

    if user.id not in [game.white_player_id, game.black_player_id]:
        await callback.answer(_('notif-not-in-game'))
        return

    t = partial(gettext_with_locale, locale=game.locale)
    total_moves = len(game.moves) if game.moves else 0

    board = reconstruct_board_at_move(game.moves or [], total_moves)

    white_name = game.white_player.first_name
    black_name = (
        game.black_player.first_name
        if game.black_player
        else "Unknown"
    )

    if game.winner_id is None:
        result_text = t('history-ended-draw')
    elif game.winner_id == game.white_player_id:
        result_text = t('history-winner-white')
    else:
        result_text = t('history-winner-black')

    text = (
        f"{t('history-header')}\n\n"
        f"{t('game-white-player', name=white_name)}\n"
        f"{t('game-black-player', name=black_name)}\n\n"
        f"{result_text}"
    )

    keyboard = create_history_board_keyboard(
        board, str(game.id), total_moves, total_moves
    )

    await _edit_history_message(callback, text, keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("hv:"))
async def handle_history_navigate(
    callback: CallbackQuery, user: User
) -> None:
    if not callback.data:
        await callback.answer(_('notif-invalid-request'))
        return

    parts = callback.data.split(":")
    if len(parts) != 3:
        await callback.answer(_('notif-invalid-request'))
        return

    game_id_str = parts[1]
    try:
        target_move = int(parts[2])
        game_id = UUID(game_id_str)
    except (ValueError, IndexError):
        await callback.answer(_('notif-invalid-request'))
        return

    game = await get_game_with_moves(game_id)
    if not game:
        await callback.answer(_('notif-game-not-found'))
        return

    if user.id not in [game.white_player_id, game.black_player_id]:
        await callback.answer(_('notif-not-in-game'))
        return

    t = partial(gettext_with_locale, locale=game.locale)
    total_moves = len(game.moves) if game.moves else 0

    if target_move < 0 or target_move > total_moves:
        await callback.answer(_('notif-invalid-request'))
        return

    board = reconstruct_board_at_move(game.moves or [], target_move)

    white_name = game.white_player.first_name
    black_name = (
        game.black_player.first_name
        if game.black_player
        else "Unknown"
    )

    if target_move == total_moves:
        if game.winner_id is None:
            turn_text = t('history-ended-draw')
        elif game.winner_id == game.white_player_id:
            turn_text = t('history-winner-white')
        else:
            turn_text = t('history-winner-black')
    elif target_move == 0:
        turn_text = t('history-initial-position')
    else:
        if target_move % 2 == 1:
            turn_text = t('history-after-white-move', move=target_move)
        else:
            turn_text = t('history-after-black-move', move=target_move)

    text = (
        f"{t('history-header')}\n\n"
        f"{t('game-white-player', name=white_name)}\n"
        f"{t('game-black-player', name=black_name)}\n\n"
        f"{turn_text}"
    )

    keyboard = create_history_board_keyboard(
        board, str(game.id), target_move, total_moves
    )

    await _edit_history_message(callback, text, keyboard)
    await callback.answer()
