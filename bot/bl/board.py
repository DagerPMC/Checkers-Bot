from typing import Dict, List, Tuple

from bot.bl.move import Move, MoveType
from bot.bl.piece import Piece, PieceColor


class Board:
    POSITIONS = [
        "a1", "c1", "e1", "g1",
        "b2", "d2", "f2", "h2",
        "a3", "c3", "e3", "g3",
        "b4", "d4", "f4", "h4",
        "a5", "c5", "e5", "g5",
        "b6", "d6", "f6", "h6",
        "a7", "c7", "e7", "g7",
        "b8", "d8", "f8", "h8",
    ]

    def __init__(self) -> None:
        self.squares: Dict[str, Piece | None] = {
            pos: None for pos in self.POSITIONS
        }
        self._setup_initial_position()

    def _setup_initial_position(self) -> None:
        white_positions = [
            "a1", "c1", "e1", "g1",
            "b2", "d2", "f2", "h2",
            "a3", "c3", "e3", "g3"
        ]
        for pos in white_positions:
            self.squares[pos] = Piece(color=PieceColor.WHITE)

        black_positions = [
            "b6", "d6", "f6", "h6",
            "a7", "c7", "e7", "g7",
            "b8", "d8", "f8", "h8"
        ]
        for pos in black_positions:
            self.squares[pos] = Piece(color=PieceColor.BLACK)

    @staticmethod
    def pos_to_coords(pos: str) -> Tuple[int, int]:
        col = ord(pos[0]) - ord('a')
        row = int(pos[1]) - 1
        return col, row

    @staticmethod
    def coords_to_pos(col: int, row: int) -> str | None:
        if not (0 <= col <= 7 and 0 <= row <= 7):
            return None
        pos = chr(ord('a') + col) + str(row + 1)
        return pos if pos in Board.POSITIONS else None

    def get_piece(self, pos: str) -> Piece | None:
        return self.squares.get(pos)

    def set_piece(self, pos: str, piece: Piece | None) -> None:
        if pos in self.squares:
            self.squares[pos] = piece

    def move_piece(self, from_pos: str, to_pos: str) -> bool:
        piece = self.get_piece(from_pos)
        if not piece:
            return False

        self.set_piece(to_pos, piece)
        self.set_piece(from_pos, None)

        col, row = self.pos_to_coords(to_pos)
        if piece.color == PieceColor.WHITE and row == 7:
            piece.promote()
        elif piece.color == PieceColor.BLACK and row == 0:
            piece.promote()

        return True

    def get_valid_moves(self, pos: str, color: PieceColor) -> List[Move]:
        piece = self.get_piece(pos)
        if not piece or piece.color != color:
            return []

        captures = self._get_single_captures(pos, piece)
        if captures:
            return captures

        if self.has_mandatory_captures(color):
            return []

        return self._get_normal_moves(pos, piece)

    def _get_normal_moves(self, pos: str, piece: Piece) -> List[Move]:
        moves = []
        col, row = self.pos_to_coords(pos)

        if piece.is_king():
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        elif piece.color == PieceColor.WHITE:
            directions = [(-1, 1), (1, 1)]
        else:
            directions = [(-1, -1), (1, -1)]

        for dc, dr in directions:
            if piece.is_king():
                distance = 1
                while True:
                    new_col = col + (dc * distance)
                    new_row = row + (dr * distance)
                    new_pos = self.coords_to_pos(new_col, new_row)

                    if not new_pos:
                        break

                    target_piece = self.get_piece(new_pos)
                    if target_piece:
                        break

                    moves.append(Move(
                        from_pos=pos,
                        to_pos=new_pos,
                        move_type=MoveType.NORMAL
                    ))
                    distance += 1
            else:
                new_col, new_row = col + dc, row + dr
                new_pos = self.coords_to_pos(new_col, new_row)

                if new_pos and not self.get_piece(new_pos):
                    moves.append(Move(
                        from_pos=pos,
                        to_pos=new_pos,
                        move_type=MoveType.NORMAL
                    ))

        return moves

    def _get_single_captures(
        self,
        pos: str,
        piece: Piece,
        excluded_positions: List[str] | None = None
    ) -> List[Move]:
        captures = []
        col, row = self.pos_to_coords(pos)

        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        excluded = excluded_positions or []

        for dc, dr in directions:
            if piece.is_king():
                direction_captures: List[Move] = []
                distance = 1
                captured_piece_pos: str | None = None

                while True:
                    check_col = col + (dc * distance)
                    check_row = row + (dr * distance)
                    check_pos = self.coords_to_pos(check_col, check_row)

                    if not check_pos:
                        break

                    # Skip excluded positions (already captured in chain)
                    if check_pos in excluded:
                        distance += 1
                        continue

                    check_piece = self.get_piece(check_pos)

                    if captured_piece_pos is None:
                        if check_piece:
                            if check_piece.color != piece.color:
                                captured_piece_pos = check_pos
                            else:
                                break
                    else:
                        if check_piece:
                            break
                        else:
                            move = Move(
                                from_pos=pos,
                                to_pos=check_pos,
                                move_type=MoveType.CAPTURE,
                                captured_positions=[captured_piece_pos]
                            )
                            direction_captures.append(move)

                    distance += 1

                # Filter: if any landing enables chain, only keep those
                if direction_captures:
                    can_continue = []
                    cannot_continue = []

                    for move in direction_captures:
                        further = self._get_single_captures(
                            move.to_pos,
                            piece,
                            move.captured_positions
                        )
                        if further:
                            can_continue.append(move)
                        else:
                            cannot_continue.append(move)

                    if can_continue:
                        captures.extend(can_continue)
                    else:
                        captures.extend(cannot_continue)
            else:
                mid_col, mid_row = col + dc, row + dr
                mid_pos = self.coords_to_pos(mid_col, mid_row)

                if not mid_pos:
                    continue

                mid_piece = self.get_piece(mid_pos)
                if not mid_piece or mid_piece.color == piece.color:
                    continue

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
        positions_with_captures = []

        for pos, piece in self.squares.items():
            if piece and piece.color == color:
                if self._get_single_captures(pos, piece):
                    positions_with_captures.append(pos)

        return positions_with_captures

    def execute_move(self, move: Move) -> bool:
        if move.is_capture and move.captured_positions:
            for cap_pos in move.captured_positions:
                self.set_piece(cap_pos, None)

        success = self.move_piece(move.from_pos, move.to_pos)

        piece = self.get_piece(move.to_pos)
        if piece and piece.is_king():
            move.promoted = True

        return success

    def get_all_valid_moves(self, color: PieceColor) -> Dict[str, List[Move]]:
        all_moves = {}

        mandatory_captures = self.has_mandatory_captures(color)

        if mandatory_captures:
            for pos in mandatory_captures:
                piece = self.get_piece(pos)
                if piece:
                    moves = self._get_single_captures(pos, piece)
                    if moves:
                        all_moves[pos] = moves
        else:
            for pos, piece in self.squares.items():
                if piece and piece.color == color:
                    moves = self._get_normal_moves(pos, piece)
                    if moves:
                        all_moves[pos] = moves

        return all_moves

    def has_valid_moves(self, color: PieceColor) -> bool:
        return len(self.get_all_valid_moves(color)) > 0

    def count_pieces(self, color: PieceColor) -> int:
        return sum(
            1 for piece in self.squares.values()
            if piece and piece.color == color
        )

    def is_game_over(self) -> Tuple[bool, PieceColor | None]:
        white_count = self.count_pieces(PieceColor.WHITE)
        black_count = self.count_pieces(PieceColor.BLACK)

        if white_count == 0:
            return True, PieceColor.BLACK
        if black_count == 0:
            return True, PieceColor.WHITE

        if not self.has_valid_moves(PieceColor.WHITE):
            return True, PieceColor.BLACK
        if not self.has_valid_moves(PieceColor.BLACK):
            return True, PieceColor.WHITE

        return False, None

    def to_dict(self) -> dict:
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
        board = cls.__new__(cls)
        board.squares = {pos: None for pos in cls.POSITIONS}

        for pos, piece_data in data.get("squares", {}).items():
            if pos in board.squares:
                board.squares[pos] = Piece.from_dict(piece_data)

        return board
