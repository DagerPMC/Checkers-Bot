from dataclasses import dataclass
from enum import StrEnum, auto


class MoveType(StrEnum):
    NORMAL = auto()
    CAPTURE = auto()


@dataclass
class Move:
    from_pos: str
    to_pos: str
    move_type: MoveType = MoveType.NORMAL
    captured_positions: list[str] | None = None
    promoted: bool = False

    def __post_init__(self):
        if self.captured_positions is None:
            self.captured_positions = []

    @property
    def is_capture(self) -> bool:
        return (
            self.move_type == MoveType.CAPTURE
            and len(self.captured_positions or []) > 0
        )
