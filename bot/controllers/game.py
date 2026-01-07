from functools import partial
from uuid import UUID

from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    ChosenInlineResult,
    InlineKeyboardButton,
)
from aiogram.types import User as TelegramUser
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import func, select

from bot.bl.board import Board
from bot.bl.game import (
    accept_game,
    cancel_game,
    create_game,
    finish_game,
    get_game,
)
from bot.bl.piece import PieceColor
from bot.db.models import Move as MoveModel
from bot.db.models import User
from bot.db.models.game import GameStatus, PlayerColor
from bot.db.session import s
from bot.middlewares.i18n import gettext as _
from bot.middlewares.i18n import gettext_with_locale
from bot.utils.keyboard import create_board_keyboard, create_invitation_keyboard


def get_user_locale(telegram_user: TelegramUser | None) -> str:
    if telegram_user and telegram_user.language_code:
        lang = telegram_user.language_code.lower().split("-")[0]
        if lang in ["uk"]:
            return "uk"
    return "en"


router = Router()


async def edit_game_message(
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


@router.chosen_inline_result()
async def handle_chosen_inline_result(
    result: ChosenInlineResult, user: User
) -> None:
    if (
        result.result_id == "checkers_invite"
        and result.inline_message_id
    ):
        pass


@router.callback_query(F.data.startswith("accept:"))
async def handle_accept_game(
    callback: CallbackQuery, user: User
) -> None:
    if not callback.data:
        await callback.answer(_('notif-invalid-request'))
        return
    game_id_str = callback.data.split(":")[1]

    if callback.message:
        chat_id = callback.message.chat.id
        message_id = callback.message.message_id
    elif callback.inline_message_id:
        chat_id = 0
        message_id = 0
    else:
        await callback.answer(_('notif-error-identify-message'))
        return

    if game_id_str == "new":
        locale = get_user_locale(callback.from_user)
        game = await create_game(
            white_player_id=user.id,
            chat_id=chat_id,
            message_id=message_id,
            locale=locale
        )
        t = partial(gettext_with_locale, locale=locale)

        text = (
            f"{t('game-header')}\n\n"
            f"{t('game-white-player', name=user.first_name)}\n"
            f"{t('game-black-waiting')}\n\n"
            f"{t('game-waiting-opponent')}"
        )

        keyboard = create_invitation_keyboard(str(game.id), locale=locale)
        await edit_game_message(callback, text, keyboard)
        await callback.answer(_('notif-game-created'))
        return

    try:
        game_id = UUID(game_id_str)
    except ValueError:
        await callback.answer(_('notif-invalid-game-id'))
        return

    maybe_game = await get_game(game_id)
    if not maybe_game:
        await callback.answer(_('notif-game-not-found'))
        return

    game = maybe_game
    if game.white_player_id == user.id:
        await callback.answer(_('notif-cant-play-yourself'))
        return

    accepted_game = await accept_game(game_id, user.id)

    if not accepted_game:
        await callback.answer(_('notif-game-already-started'))
        return

    t = partial(gettext_with_locale, locale=accepted_game.locale)
    board = Board.from_dict(accepted_game.board_state)

    white_name = accepted_game.white_player.first_name
    black_name = (
        accepted_game.black_player.first_name
        if accepted_game.black_player
        else "Unknown"
    )

    text = (
        f"{t('game-header')}\n\n"
        f"{t('game-white-player', name=white_name)}\n"
        f"{t('game-black-player', name=black_name)}\n\n"
        f"{t('game-current-turn-white')}"
    )

    keyboard = create_board_keyboard(
        board, str(accepted_game.id), PieceColor.WHITE,
        locale=accepted_game.locale
    )
    await edit_game_message(callback, text, keyboard)
    await callback.answer(_('notif-game-started'))


@router.callback_query(F.data.startswith("cancel:"))
async def handle_cancel_game(
    callback: CallbackQuery, user: User
) -> None:
    if not callback.data:
        await callback.answer(_('notif-invalid-request'))
        return
    game_id_str = callback.data.split(":")[1]

    if game_id_str == "new":
        await edit_game_message(callback, _('game-cancelled'))
        await callback.answer(_('notif-game-cancelled'))
        return

    try:
        game_id = UUID(game_id_str)
    except ValueError:
        await callback.answer(_('notif-invalid-game-id'))
        return

    game = await get_game(game_id)
    if game:
        t = partial(gettext_with_locale, locale=game.locale)
        success = await cancel_game(game_id)
        if success:
            await edit_game_message(callback, t('game-cancelled'))
            await callback.answer(_('notif-game-cancelled'))
        else:
            await callback.answer(_('notif-failed-cancel'))
    else:
        await callback.answer(_('notif-game-not-found'))


@router.callback_query(F.data.startswith("select:"))
async def handle_select_piece(
    callback: CallbackQuery, user: User
) -> None:
    if not callback.data:
        await callback.answer(_('notif-invalid-request'))
        return
    parts = callback.data.split(":")
    game_id = UUID(parts[1])
    position = parts[2]

    game = await get_game(game_id)
    if not game:
        await callback.answer(_('notif-game-not-found'))
        return

    t = partial(gettext_with_locale, locale=game.locale)
    current_color = (
        PieceColor.WHITE
        if game.current_turn == PlayerColor.WHITE
        else PieceColor.BLACK
    )
    if (
        (current_color == PieceColor.WHITE
         and game.white_player_id != user.id)
        or (current_color == PieceColor.BLACK
            and game.black_player_id != user.id)
    ):
        await callback.answer(_('notif-not-your-turn'))
        return

    board = Board.from_dict(game.board_state)

    white_name = game.white_player.first_name
    black_name = (
        game.black_player.first_name
        if game.black_player
        else "Unknown"
    )
    turn_emoji = "⚪" if game.current_turn == PlayerColor.WHITE else "⚫"
    turn_color = t(
        'color-white' if game.current_turn == PlayerColor.WHITE
        else 'color-black'
    )

    text = (
        f"{t('game-header')}\n\n"
        f"{t('game-white-player', name=white_name)}\n"
        f"{t('game-black-player', name=black_name)}\n\n"
        f"{t('game-current-turn', emoji=turn_emoji, color=turn_color)}"
    )

    keyboard = create_board_keyboard(
        board, str(game.id), current_color, selected_pos=position,
        locale=game.locale
    )
    await edit_game_message(callback, text, keyboard)
    await callback.answer(_('notif-selected-position', position=position))


@router.callback_query(F.data.startswith("deselect:"))
async def handle_deselect_piece(
    callback: CallbackQuery, user: User
) -> None:
    if not callback.data:
        await callback.answer(_('notif-invalid-request'))
        return
    game_id = UUID(callback.data.split(":")[1])

    game = await get_game(game_id)
    if not game:
        await callback.answer(_('notif-game-not-found'))
        return

    t = partial(gettext_with_locale, locale=game.locale)
    board = Board.from_dict(game.board_state)
    current_color = (
        PieceColor.WHITE
        if game.current_turn == PlayerColor.WHITE
        else PieceColor.BLACK
    )

    white_name = game.white_player.first_name
    black_name = (
        game.black_player.first_name
        if game.black_player
        else "Unknown"
    )
    turn_emoji = "⚪" if game.current_turn == PlayerColor.WHITE else "⚫"
    turn_color = t(
        'color-white' if game.current_turn == PlayerColor.WHITE
        else 'color-black'
    )

    text = (
        f"{t('game-header')}\n\n"
        f"{t('game-white-player', name=white_name)}\n"
        f"{t('game-black-player', name=black_name)}\n\n"
        f"{t('game-current-turn', emoji=turn_emoji, color=turn_color)}"
    )

    keyboard = create_board_keyboard(
        board, str(game.id), current_color, locale=game.locale
    )
    await edit_game_message(callback, text, keyboard)
    await callback.answer(_('notif-deselected'))


@router.callback_query(F.data.startswith("move:"))
async def handle_move(
    callback: CallbackQuery, user: User
) -> None:
    if not callback.data:
        await callback.answer(_('notif-invalid-request'))
        return
    parts = callback.data.split(":")
    game_id = UUID(parts[1])
    move_str = parts[2]
    from_pos, to_pos = move_str.split("-")

    game = await get_game(game_id)
    if not game:
        await callback.answer(_('notif-game-not-found'))
        return

    t = partial(gettext_with_locale, locale=game.locale)
    current_color = (
        PieceColor.WHITE
        if game.current_turn == PlayerColor.WHITE
        else PieceColor.BLACK
    )
    if (
        (current_color == PieceColor.WHITE
         and game.white_player_id != user.id)
        or (current_color == PieceColor.BLACK
            and game.black_player_id != user.id)
    ):
        await callback.answer(_('notif-not-your-turn'))
        return

    board = Board.from_dict(game.board_state)

    valid_moves = board.get_valid_moves(from_pos, current_color)
    move = next((m for m in valid_moves if m.to_pos == to_pos), None)

    if not move:
        await callback.answer(_('notif-invalid-move'))
        return

    board.execute_move(move)

    move_count_result = await s.session.execute(
        select(func.count(MoveModel.id)).where(MoveModel.game_id == game.id)
    )
    move_count = move_count_result.scalar() or 0

    db_move = MoveModel(
        game_id=game.id,
        player_id=user.id,
        from_position=from_pos,
        to_position=to_pos,
        captured_positions=(
            move.captured_positions if move.captured_positions else None
        ),
        promoted=move.promoted,
        move_number=move_count + 1
    )
    s.session.add(db_move)

    continue_capturing = False
    if move.is_capture:
        piece = board.get_piece(to_pos)
        if piece:
            further_captures = board._get_single_captures(to_pos, piece)
            if further_captures:
                continue_capturing = True

    is_over, winner_color = board.is_game_over()

    if is_over:
        winner_id = None
        if winner_color == PieceColor.WHITE:
            winner_id = game.white_player_id
        elif winner_color == PieceColor.BLACK:
            winner_id = game.black_player_id

        await finish_game(game_id, winner_id)

        winner_name = t(
            'color-white' if winner_color == PieceColor.WHITE
            else 'color-black'
        )
        black_name = (
            game.black_player.first_name
            if game.black_player
            else 'Unknown'
        )
        text = (
            f"{t('game-header-finished')}\n\n"
            f"{t('game-white-player', name=game.white_player.first_name)}\n"
            f"{t('game-black-player', name=black_name)}\n\n"
            f"{t('game-winner', name=winner_name)}"
        )

        await edit_game_message(callback, text)
        await callback.answer(_('notif-game-over', winner=winner_name))
        return

    game.board_state = board.to_dict()

    if not continue_capturing:
        game.current_turn = (
            PlayerColor.BLACK
            if game.current_turn == PlayerColor.WHITE
            else PlayerColor.WHITE
        )

    if continue_capturing:
        keyboard = create_board_keyboard(
            board, str(game.id), current_color, selected_pos=to_pos,
            locale=game.locale
        )
        if callback.message and hasattr(callback.message, 'edit_reply_markup'):
            await callback.message.edit_reply_markup(reply_markup=keyboard)
        elif callback.inline_message_id and callback.bot:
            await callback.bot.edit_message_reply_markup(
                inline_message_id=callback.inline_message_id,
                reply_markup=keyboard
            )
    else:
        white_name = game.white_player.first_name
        black_name = (
            game.black_player.first_name
            if game.black_player
            else "Unknown"
        )
        turn_emoji = (
            "⚪" if game.current_turn == PlayerColor.WHITE else "⚫"
        )
        turn_color = t(
            'color-white' if game.current_turn == PlayerColor.WHITE
            else 'color-black'
        )
        next_color = (
            PieceColor.WHITE
            if game.current_turn == PlayerColor.WHITE
            else PieceColor.BLACK
        )
        text = (
            f"{t('game-header')}\n\n"
            f"{t('game-white-player', name=white_name)}\n"
            f"{t('game-black-player', name=black_name)}\n\n"
            f"{t('game-current-turn', emoji=turn_emoji, color=turn_color)}"
        )
        keyboard = create_board_keyboard(
            board, str(game.id), next_color, locale=game.locale
        )
        await edit_game_message(callback, text, keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("draw:"))
async def handle_draw_proposal(
    callback: CallbackQuery, user: User
) -> None:
    if not callback.data:
        await callback.answer(_('notif-invalid-request'))
        return
    game_id = UUID(callback.data.split(":")[1])

    game = await get_game(game_id)
    if not game:
        await callback.answer(_('notif-game-not-found'))
        return

    if game.status != GameStatus.ACTIVE:
        await callback.answer(_('notif-game-not-active'))
        return

    if user.id not in [game.white_player_id, game.black_player_id]:
        await callback.answer(_('notif-not-in-game'))
        return

    await callback.answer(_('notif-draw-proposal-sent'), show_alert=True)

    t = partial(gettext_with_locale, locale=game.locale)
    white_name = game.white_player.first_name
    black_name = (
        game.black_player.first_name
        if game.black_player
        else "Unknown"
    )
    turn_emoji = "⚪" if game.current_turn == PlayerColor.WHITE else "⚫"
    turn_color = t(
        'color-white' if game.current_turn == PlayerColor.WHITE
        else 'color-black'
    )
    proposer_name = user.first_name

    text = (
        f"{t('game-header')}\n\n"
        f"{t('game-white-player', name=white_name)}\n"
        f"{t('game-black-player', name=black_name)}\n\n"
        f"{t('game-current-turn', emoji=turn_emoji, color=turn_color)}\n\n"
        f"{t('game-draw-proposal', name=proposer_name)}"
    )

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t('btn-accept-draw'),
            callback_data=f"draw_accept:{game_id}"
        ),
        InlineKeyboardButton(
            text=t('btn-decline-draw'),
            callback_data=f"draw_decline:{game_id}"
        )
    )

    await edit_game_message(callback, text, builder.as_markup())


@router.callback_query(F.data.startswith("draw_accept:"))
async def handle_draw_accept(
    callback: CallbackQuery, user: User
) -> None:
    if not callback.data:
        await callback.answer(_('notif-invalid-request'))
        return
    game_id = UUID(callback.data.split(":")[1])

    game = await finish_game(game_id, None)

    if game:
        t = partial(gettext_with_locale, locale=game.locale)
        black_name = (
            game.black_player.first_name
            if game.black_player
            else 'Unknown'
        )
        text = (
            f"{t('game-header-draw')}\n\n"
            f"{t('game-white-player', name=game.white_player.first_name)}\n"
            f"{t('game-black-player', name=black_name)}\n\n"
            f"{t('game-draw-ended')}"
        )

        await edit_game_message(callback, text)
        await callback.answer(_('notif-draw-accepted'))
    else:
        await callback.answer(_('notif-error-accepting-draw'))


@router.callback_query(F.data.startswith("draw_decline:"))
async def handle_draw_decline(
    callback: CallbackQuery, user: User
) -> None:
    if not callback.data:
        await callback.answer(_('notif-invalid-request'))
        return
    game_id = UUID(callback.data.split(":")[1])

    game = await get_game(game_id)
    if not game:
        await callback.answer(_('notif-game-not-found'))
        return

    t = partial(gettext_with_locale, locale=game.locale)
    board = Board.from_dict(game.board_state)
    current_color = (
        PieceColor.WHITE
        if game.current_turn == PlayerColor.WHITE
        else PieceColor.BLACK
    )

    white_name = game.white_player.first_name
    black_name = (
        game.black_player.first_name
        if game.black_player
        else "Unknown"
    )
    turn_emoji = "⚪" if game.current_turn == PlayerColor.WHITE else "⚫"
    turn_color = t(
        'color-white' if game.current_turn == PlayerColor.WHITE
        else 'color-black'
    )

    text = (
        f"{t('game-header')}\n\n"
        f"{t('game-white-player', name=white_name)}\n"
        f"{t('game-black-player', name=black_name)}\n\n"
        f"{t('game-current-turn', emoji=turn_emoji, color=turn_color)}"
    )

    keyboard = create_board_keyboard(
        board, str(game.id), current_color, locale=game.locale
    )
    await edit_game_message(callback, text, keyboard)
    await callback.answer(_('notif-draw-declined'))


@router.callback_query(F.data.startswith("surrender:"))
async def handle_surrender(
    callback: CallbackQuery, user: User
) -> None:
    if not callback.data:
        await callback.answer(_('notif-invalid-request'))
        return
    game_id = UUID(callback.data.split(":")[1])

    game = await get_game(game_id)
    if not game:
        await callback.answer(_('notif-game-not-found'))
        return

    if game.status != GameStatus.ACTIVE:
        await callback.answer(_('notif-game-not-active'))
        return

    if user.id not in [game.white_player_id, game.black_player_id]:
        await callback.answer(_('notif-not-in-game'))
        return

    await callback.answer()

    t = partial(gettext_with_locale, locale=game.locale)
    white_name = game.white_player.first_name
    black_name = (
        game.black_player.first_name
        if game.black_player
        else "Unknown"
    )
    turn_emoji = "⚪" if game.current_turn == PlayerColor.WHITE else "⚫"
    turn_color = t(
        'color-white' if game.current_turn == PlayerColor.WHITE
        else 'color-black'
    )

    text = (
        f"{t('game-header')}\n\n"
        f"{t('game-white-player', name=white_name)}\n"
        f"{t('game-black-player', name=black_name)}\n\n"
        f"{t('game-current-turn', emoji=turn_emoji, color=turn_color)}\n\n"
        f"{t('game-surrender-proposal', name=user.first_name)}"
    )

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t('btn-confirm-surrender'),
            callback_data=f"surrender_confirm:{game_id}"
        ),
        InlineKeyboardButton(
            text=t('btn-cancel'),
            callback_data=f"surrender_cancel:{game_id}"
        )
    )

    await edit_game_message(callback, text, builder.as_markup())


@router.callback_query(F.data.startswith("surrender_confirm:"))
async def handle_surrender_confirm(
    callback: CallbackQuery, user: User
) -> None:
    if not callback.data:
        await callback.answer(_('notif-invalid-request'))
        return
    game_id = UUID(callback.data.split(":")[1])

    game = await get_game(game_id)
    if not game:
        await callback.answer(_('notif-game-not-found'))
        return

    t = partial(gettext_with_locale, locale=game.locale)
    if user.id == game.white_player_id:
        winner_id = game.black_player_id
        winner_name = t('color-black')
    else:
        winner_id = game.white_player_id
        winner_name = t('color-white')

    await finish_game(game_id, winner_id)

    black_name = (
        game.black_player.first_name
        if game.black_player
        else 'Unknown'
    )
    text = (
        f"{t('game-header-finished')}\n\n"
        f"{t('game-white-player', name=game.white_player.first_name)}\n"
        f"{t('game-black-player', name=black_name)}\n\n"
        f"{t('game-winner-by-surrender', name=winner_name)}"
    )

    await edit_game_message(callback, text)
    await callback.answer(_('notif-surrender-winner', winner=winner_name))


@router.callback_query(F.data.startswith("surrender_cancel:"))
async def handle_surrender_cancel(
    callback: CallbackQuery, user: User
) -> None:
    if not callback.data:
        await callback.answer(_('notif-invalid-request'))
        return
    game_id = UUID(callback.data.split(":")[1])

    game = await get_game(game_id)
    if not game:
        await callback.answer(_('notif-game-not-found'))
        return

    t = partial(gettext_with_locale, locale=game.locale)
    board = Board.from_dict(game.board_state)
    current_color = (
        PieceColor.WHITE
        if game.current_turn == PlayerColor.WHITE
        else PieceColor.BLACK
    )

    white_name = game.white_player.first_name
    black_name = (
        game.black_player.first_name
        if game.black_player
        else "Unknown"
    )
    turn_emoji = "⚪" if game.current_turn == PlayerColor.WHITE else "⚫"
    turn_color = t(
        'color-white' if game.current_turn == PlayerColor.WHITE
        else 'color-black'
    )

    text = (
        f"{t('game-header')}\n\n"
        f"{t('game-white-player', name=white_name)}\n"
        f"{t('game-black-player', name=black_name)}\n\n"
        f"{t('game-current-turn', emoji=turn_emoji, color=turn_color)}"
    )

    keyboard = create_board_keyboard(
        board, str(game.id), current_color, locale=game.locale
    )
    await edit_game_message(callback, text, keyboard)
    await callback.answer(_('notif-surrender-cancelled'))


@router.callback_query(F.data == "noop")
async def handle_noop(callback: CallbackQuery) -> None:
    await callback.answer()
