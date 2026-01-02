from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.bl.board import Board
from bot.bl.piece import PieceColor


def create_invitation_keyboard(game_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="✅ Accept & Join",
            callback_data=f"accept:{game_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="❌ Cancel",
            callback_data=f"cancel:{game_id}"
        )
    )

    return builder.as_markup()


def create_board_keyboard(
    board: Board,
    game_id: str,
    current_turn: PieceColor,
    selected_pos: str | None = None
) -> InlineKeyboardMarkup:
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
            text="🏳️ Propose Draw",
            callback_data=f"draw:{game_id}"
        ),
        InlineKeyboardButton(
            text="🏴 Surrender",
            callback_data=f"surrender:{game_id}"
        )
    )

    return builder.as_markup()
