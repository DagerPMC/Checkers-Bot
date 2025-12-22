from dataclasses import dataclass
from enum import StrEnum, auto


class MoveType(StrEnum):
    NORMAL = auto()
    CAPTURE = auto()


@dataclass
class Move:
    """Represents a single move in checkers."""
    from_pos: str  # e.g., "a3"
    to_pos: str    # e.g., "b4"
    move_type: MoveType = MoveType.NORMAL
    captured_positions: list[str] | None = None
    promoted: bool = False

    def __post_init__(self):
        if self.captured_positions is None:
            self.captured_positions = []

    @property
    def is_capture(self) -> bool:
        """Check if this move captures any pieces."""
        return self.move_type == MoveType.CAPTURE and len(self.captured_positions or []) > 0
