from dataclasses import dataclass
from enum import StrEnum, auto


class PieceColor(StrEnum):
    WHITE = auto()
    BLACK = auto()


class PieceType(StrEnum):
    REGULAR = auto()
    KING = auto()


@dataclass
class Piece:
    color: PieceColor
    type: PieceType = PieceType.REGULAR

    def promote(self) -> None:
        self.type = PieceType.KING

    def is_king(self) -> bool:
        return self.type == PieceType.KING

    def to_emoji(self) -> str:
        if self.color == PieceColor.WHITE:
            return "⬜" if self.is_king() else "⚪"
        else:
            return "⬛" if self.is_king() else "⚫"

    def to_dict(self) -> dict:
        return {
            "color": self.color.value,
            "king": self.is_king()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Piece':
        color = PieceColor(data["color"])
        piece_type = PieceType.KING if data["king"] else PieceType.REGULAR
        return cls(color=color, type=piece_type)
