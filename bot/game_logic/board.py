from typing import Dict, List, Tuple

from bot.game_logic.piece import Piece, PieceColor, PieceType
from bot.game_logic.move import Move, MoveType


class Board:
    """Represents a checkers board."""

    # Board positions (only dark squares are playable)
    POSITIONS = [
        # Row 1 (white side)
        "a1", "c1", "e1", "g1",
        # Row 2
        "b2", "d2", "f2", "h2",
        # Row 3
        "a3", "c3", "e3", "g3",
        # Row 4
        "b4", "d4", "f4", "h4",
        # Row 5
        "a5", "c5", "e5", "g5",
        # Row 6
        "b6", "d6", "f6", "h6",
        # Row 7
        "a7", "c7", "e7", "g7",
        # Row 8 (black side)
        "b8", "d8", "f8", "h8",
    ]

    def __init__(self):
        self.squares: Dict[str, Piece | None] = {pos: None for pos in self.POSITIONS}
        self._setup_initial_position()

    def _setup_initial_position(self) -> None:
        """Set up the initial checkers position."""
        # White pieces (rows 1-3)
        white_positions = [
            "a1", "c1", "e1", "g1",
            "b2", "d2", "f2", "h2",
            "a3", "c3", "e3", "g3"
        ]
        for pos in white_positions:
            self.squares[pos] = Piece(color=PieceColor.WHITE)

        # Black pieces (rows 6-8)
        black_positions = [
            "b6", "d6", "f6", "h6",
            "a7", "c7", "e7", "g7",
            "b8", "d8", "f8", "h8"
        ]
        for pos in black_positions:
            self.squares[pos] = Piece(color=PieceColor.BLACK)

    @staticmethod
    def pos_to_coords(pos: str) -> Tuple[int, int]:
        """Convert position like 'a1' to coordinates (col, row)."""
        col = ord(pos[0]) - ord('a')
        row = int(pos[1]) - 1
        return col, row

    @staticmethod
    def coords_to_pos(col: int, row: int) -> str | None:
        """Convert coordinates to position like 'a1'."""
        if not (0 <= col <= 7 and 0 <= row <= 7):
            return None
        pos = chr(ord('a') + col) + str(row + 1)
        return pos if pos in Board.POSITIONS else None

    def get_piece(self, pos: str) -> Piece | None:
        """Get piece at position."""
        return self.squares.get(pos)

    def set_piece(self, pos: str, piece: Piece | None) -> None:
        """Set piece at position."""
        if pos in self.squares:
            self.squares[pos] = piece

    def move_piece(self, from_pos: str, to_pos: str) -> bool:
        """Move piece from one position to another."""
        piece = self.get_piece(from_pos)
        if not piece:
            return False

        self.set_piece(to_pos, piece)
        self.set_piece(from_pos, None)

        # Check for promotion
        col, row = self.pos_to_coords(to_pos)
        if piece.color == PieceColor.WHITE and row == 7:
            piece.promote()
        elif piece.color == PieceColor.BLACK and row == 0:
            piece.promote()

        return True

    def get_valid_moves(self, pos: str, color: PieceColor) -> List[Move]:
        """Get all valid moves for a piece at the given position."""
        piece = self.get_piece(pos)
        if not piece or piece.color != color:
            return []

        # First check for captures (mandatory in checkers)
        # Return only single jumps, not complete chains
        captures = self._get_single_captures(pos, piece)
        if captures:
            return captures

        # If no captures available, check if ANY piece of this color has captures
        # If so, this piece cannot move
        if self.has_mandatory_captures(color):
            return []

        # No captures available for any piece, return normal moves
        return self._get_normal_moves(pos, piece)

    def _get_normal_moves(self, pos: str, piece: Piece) -> List[Move]:
        """Get all normal (non-capturing) moves for a piece."""
        moves = []
        col, row = self.pos_to_coords(pos)

        # Determine move directions based on piece type and color
        if piece.is_king():
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # All diagonals
        elif piece.color == PieceColor.WHITE:
            directions = [(-1, 1), (1, 1)]  # Forward for white
        else:
            directions = [(-1, -1), (1, -1)]  # Forward for black

        for dc, dr in directions:
            if piece.is_king():
                # Kings can move multiple squares along a diagonal
                distance = 1
                while True:
                    new_col = col + (dc * distance)
                    new_row = row + (dr * distance)
                    new_pos = self.coords_to_pos(new_col, new_row)

                    if not new_pos:
                        # Reached edge of board
                        break

                    target_piece = self.get_piece(new_pos)
                    if target_piece:
                        # Blocked by another piece
                        break

                    # Empty square - valid move
                    moves.append(Move(from_pos=pos, to_pos=new_pos, move_type=MoveType.NORMAL))
                    distance += 1
            else:
                # Regular pieces move one square
                new_col, new_row = col + dc, row + dr
                new_pos = self.coords_to_pos(new_col, new_row)

                if new_pos and not self.get_piece(new_pos):
                    moves.append(Move(from_pos=pos, to_pos=new_pos, move_type=MoveType.NORMAL))

        return moves

    def _get_single_captures(self, pos: str, piece: Piece) -> List[Move]:
        """Get all single jump captures from a position (not chains)."""
        captures = []
        col, row = self.pos_to_coords(pos)

        # ALL pieces can capture in all diagonal directions (including backwards)
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dc, dr in directions:
            if piece.is_king():
                # Kings can capture from any distance along a diagonal
                # and land on any empty square beyond the captured piece
                distance = 1
                captured_piece_pos = None
                captured_at_distance = None

                while True:
                    check_col = col + (dc * distance)
                    check_row = row + (dr * distance)
                    check_pos = self.coords_to_pos(check_col, check_row)

                    if not check_pos:
                        # Reached edge
                        break

                    check_piece = self.get_piece(check_pos)

                    if captured_piece_pos is None:
                        # Still looking for a piece to capture
                        if check_piece:
                            if check_piece.color != piece.color:
                                # Found opponent piece to capture
                                captured_piece_pos = check_pos
                                captured_at_distance = distance
                            else:
                                # Blocked by own piece
                                break
                    else:
                        # Already found piece to capture, now looking for landing squares
                        if check_piece:
                            # Another piece blocking - can't land here
                            break
                        else:
                            # Empty square after captured piece - valid landing
                            move = Move(
                                from_pos=pos,
                                to_pos=check_pos,
                                move_type=MoveType.CAPTURE,
                                captured_positions=[captured_piece_pos]
                            )
                            captures.append(move)

                    distance += 1
            else:
                # Regular pieces capture by jumping over adjacent opponent
                mid_col, mid_row = col + dc, row + dr
                mid_pos = self.coords_to_pos(mid_col, mid_row)

                if not mid_pos:
                    continue

                mid_piece = self.get_piece(mid_pos)
                if not mid_piece or mid_piece.color == piece.color:
                    continue

                # Check if landing square is empty (must be immediately after)
                land_col, land_row = mid_col + dc, mid_row + dr
                land_pos = self.coords_to_pos(land_col, land_row)

                if land_pos and not self.get_piece(land_pos):
                    move = Move(
                        from_pos=pos,
                        to_pos=land_pos,
                        move_type=MoveType.CAPTURE,
                        captured_positions=[mid_pos]
                    )
                    captures.append(move)

        return captures

    def has_mandatory_captures(self, color: PieceColor) -> List[str]:
        """Get positions of pieces that have mandatory captures."""
        positions_with_captures = []

        for pos, piece in self.squares.items():
            if piece and piece.color == color:
                if self._get_single_captures(pos, piece):
                    positions_with_captures.append(pos)

        return positions_with_captures

    def execute_move(self, move: Move) -> bool:
        """Execute a move on the board."""
        # Remove captured pieces
        if move.is_capture and move.captured_positions:
            for cap_pos in move.captured_positions:
                self.set_piece(cap_pos, None)

        # Move the piece
        success = self.move_piece(move.from_pos, move.to_pos)

        # Check if promoted
        piece = self.get_piece(move.to_pos)
        if piece and piece.is_king():
            move.promoted = True

        return success

    def get_all_valid_moves(self, color: PieceColor) -> Dict[str, List[Move]]:
        """Get all valid moves for all pieces of a color."""
        all_moves = {}

        # Check if there are mandatory captures
        mandatory_captures = self.has_mandatory_captures(color)

        if mandatory_captures:
            # Only return capture moves from pieces that can capture
            for pos in mandatory_captures:
                piece = self.get_piece(pos)
                if piece:
                    moves = self._get_single_captures(pos, piece)
                    if moves:
                        all_moves[pos] = moves
        else:
            # Return all normal moves
            for pos, piece in self.squares.items():
                if piece and piece.color == color:
                    moves = self._get_normal_moves(pos, piece)
                    if moves:
                        all_moves[pos] = moves

        return all_moves

    def has_valid_moves(self, color: PieceColor) -> bool:
        """Check if a player has any valid moves."""
        return len(self.get_all_valid_moves(color)) > 0

    def count_pieces(self, color: PieceColor) -> int:
        """Count pieces of a given color."""
        return sum(1 for piece in self.squares.values() if piece and piece.color == color)

    def is_game_over(self) -> Tuple[bool, PieceColor | None]:
        """
        Check if game is over.
        Returns (is_over, winner_color)
        """
        white_count = self.count_pieces(PieceColor.WHITE)
        black_count = self.count_pieces(PieceColor.BLACK)

        # No pieces left
        if white_count == 0:
            return True, PieceColor.BLACK
        if black_count == 0:
            return True, PieceColor.WHITE

        # No valid moves (stalemate = loss)
        if not self.has_valid_moves(PieceColor.WHITE):
            return True, PieceColor.BLACK
        if not self.has_valid_moves(PieceColor.BLACK):
            return True, PieceColor.WHITE

        return False, None

    def to_dict(self) -> dict:
        """Convert board state to dictionary for JSON storage."""
        squares_dict = {}
        for pos, piece in self.squares.items():
            if piece:
                squares_dict[pos] = piece.to_dict()

        must_capture = self.has_mandatory_captures(PieceColor.WHITE)
        must_capture.extend(self.has_mandatory_captures(PieceColor.BLACK))

        return {
            "squares": squares_dict,
            "must_capture": must_capture
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Board':
        """Create board from dictionary."""
        board = cls.__new__(cls)
        board.squares = {pos: None for pos in cls.POSITIONS}

        for pos, piece_data in data.get("squares", {}).items():
            if pos in board.squares:
                board.squares[pos] = Piece.from_dict(piece_data)

        return board
