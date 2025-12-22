from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.game_logic.board import Board
from bot.game_logic.piece import PieceColor


def create_invitation_keyboard(game_id: str) -> InlineKeyboardMarkup:
    """Create keyboard for game invitation."""
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
    """
    Create inline keyboard representing the checkers board.

    Args:
        board: The current board state
        game_id: Game identifier
        current_turn: Which player's turn it is
        selected_pos: Currently selected piece position (if any)
    """
    builder = InlineKeyboardBuilder()

    # Get valid moves if a piece is selected
    valid_moves = []
    if selected_pos:
        piece = board.get_piece(selected_pos)
        if piece and piece.color == current_turn:
            valid_moves = board.get_valid_moves(selected_pos, current_turn)

    # Create board rows (8 rows, top to bottom)
    for row in range(7, -1, -1):  # Start from row 8 down to row 1
        row_buttons = []

        for col in range(8):
            pos = Board.coords_to_pos(col, row)

            # Light squares (not playable) - show as empty
            if not pos or pos not in board.squares:
                row_buttons.append(
                    InlineKeyboardButton(
                        text="  ",
                        callback_data="noop"
                    )
                )
                continue

            piece = board.get_piece(pos)

            # Determine button text and callback
            if selected_pos == pos:
                # Currently selected piece - show with highlight
                button_text = f"[{piece.to_emoji()}]" if piece else "[•]"
                callback_data = f"deselect:{game_id}"
            elif selected_pos and any(m.to_pos == pos for m in valid_moves):
                # Valid move destination
                button_text = "🟢"
                callback_data = f"move:{game_id}:{selected_pos}-{pos}"
            elif piece:
                # Piece on the board
                button_text = piece.to_emoji()
                # Only allow selection if it's this piece's turn AND it has valid moves
                if piece.color == current_turn:
                    piece_moves = board.get_valid_moves(pos, current_turn)
                    if piece_moves:
                        callback_data = f"select:{game_id}:{pos}"
                    else:
                        callback_data = "noop"
                else:
                    callback_data = "noop"
            else:
                # Empty playable square
                button_text = "•"
                callback_data = "noop"

            row_buttons.append(
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=callback_data
                )
            )

        builder.row(*row_buttons)

    # Add game control buttons at the bottom
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
