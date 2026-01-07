from functools import partial

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.bl.board import Board
from bot.bl.piece import PieceColor
from bot.middlewares.i18n import gettext_with_locale


def create_invitation_keyboard(
    game_id: str,
    locale: str = 'en'
) -> InlineKeyboardMarkup:
    _ = partial(gettext_with_locale, locale=locale)
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_('btn-accept-join'),
            callback_data=f"accept:{game_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_('btn-cancel'),
            callback_data=f"cancel:{game_id}"
        )
    )

    return builder.as_markup()


def create_board_keyboard(
    board: Board,
    game_id: str,
    current_turn: PieceColor,
    selected_pos: str | None = None,
    locale: str = 'en'
) -> InlineKeyboardMarkup:
    _ = partial(gettext_with_locale, locale=locale)
    builder = InlineKeyboardBuilder()

    valid_moves = []
    if selected_pos:
        piece = board.get_piece(selected_pos)
        if piece and piece.color == current_turn:
            valid_moves = board.get_valid_moves(selected_pos, current_turn)

    for row in range(7, -1, -1):
        row_buttons = []

        for col in range(8):
            pos = Board.coords_to_pos(col, row)

            if not pos or pos not in board.squares:
                row_buttons.append(
                    InlineKeyboardButton(
                        text="  ",
                        callback_data="noop"
                    )
                )
                continue

            piece = board.get_piece(pos)

            if selected_pos == pos:
                button_text = f"[{piece.to_emoji()}]" if piece else "[•]"
                callback_data = f"deselect:{game_id}"
            elif selected_pos and any(m.to_pos == pos for m in valid_moves):
                button_text = "🟢"
                callback_data = f"move:{game_id}:{selected_pos}-{pos}"
            elif piece:
                button_text = piece.to_emoji()
                if piece.color == current_turn:
                    piece_moves = board.get_valid_moves(pos, current_turn)
                    if piece_moves:
                        callback_data = f"select:{game_id}:{pos}"
                    else:
                        callback_data = "noop"
                else:
                    callback_data = "noop"
            else:
                button_text = "•"
                callback_data = "noop"

            row_buttons.append(
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=callback_data
                )
            )

        builder.row(*row_buttons)

    builder.row(
        InlineKeyboardButton(
            text=_('btn-propose-draw'),
            callback_data=f"draw:{game_id}"
        ),
        InlineKeyboardButton(
            text=_('btn-surrender'),
            callback_data=f"surrender:{game_id}"
        )
    )

    return builder.as_markup()


def create_history_board_keyboard(
    board: Board,
    game_id: str,
    current_move: int,
    total_moves: int
) -> InlineKeyboardMarkup:
    """Create non-interactive board with navigation buttons for history."""
    builder = InlineKeyboardBuilder()

    for row in range(7, -1, -1):
        row_buttons = []

        for col in range(8):
            pos = Board.coords_to_pos(col, row)

            if not pos or pos not in board.squares:
                row_buttons.append(
                    InlineKeyboardButton(text="  ", callback_data="noop")
                )
                continue

            piece = board.get_piece(pos)
            button_text = piece.to_emoji() if piece else "•"
            row_buttons.append(
                InlineKeyboardButton(text=button_text, callback_data="noop")
            )

        builder.row(*row_buttons)

    # Navigation row: ⏮ ◀ [5/24] ▶ ⏭
    nav_buttons = []

    # Jump to start
    nav_buttons.append(InlineKeyboardButton(
        text="⏮",
        callback_data=f"hv:{game_id}:0" if current_move > 0 else "noop"
    ))

    # Previous move
    nav_buttons.append(InlineKeyboardButton(
        text="◀",
        callback_data=(
            f"hv:{game_id}:{current_move - 1}" if current_move > 0 else "noop"
        )
    ))

    # Move counter
    nav_buttons.append(InlineKeyboardButton(
        text=f"{current_move}/{total_moves}",
        callback_data="noop"
    ))

    # Next move
    nav_buttons.append(InlineKeyboardButton(
        text="▶",
        callback_data=(
            f"hv:{game_id}:{current_move + 1}"
            if current_move < total_moves
            else "noop"
        )
    ))

    # Jump to end
    nav_buttons.append(InlineKeyboardButton(
        text="⏭",
        callback_data=(
            f"hv:{game_id}:{total_moves}"
            if current_move < total_moves
            else "noop"
        )
    ))

    builder.row(*nav_buttons)

    return builder.as_markup()
