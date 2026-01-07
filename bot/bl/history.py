from typing import TYPE_CHECKING

from bot.bl.board import Board
from bot.bl.move import Move, MoveType

if TYPE_CHECKING:
    from bot.db.models import Move as MoveModel


def reconstruct_board_at_move(
    moves: list['MoveModel'],
    target_move: int
) -> Board:
    """
    Reconstruct board state at a specific move number.

    Args:
        moves: List of Move model instances, ordered by move_number
        target_move: The move number to reconstruct to (0 = initial position)

    Returns:
        Board at the specified move state
    """
    board = Board()

    for move_record in moves:
        if move_record.move_number > target_move:
            break

        captured = move_record.captured_positions or []
        move = Move(
            from_pos=move_record.from_position,
            to_pos=move_record.to_position,
            move_type=MoveType.CAPTURE if captured else MoveType.NORMAL,
            captured_positions=captured,
            promoted=move_record.promoted
        )
        board.execute_move(move)

    return board
