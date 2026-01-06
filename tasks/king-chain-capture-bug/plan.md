# Implementation Plan: King Chain Capture Bug Fix

## Problem Analysis

The bug is in `_get_single_captures()` method in `/home/dager/projects/personal/checkers/bot/bl/board.py` (lines 137-200). For king captures, the method currently returns ALL empty squares along the diagonal after jumping over an enemy piece, without checking whether landing on each square would enable a chain capture.

According to checkers rules, if any landing square allows a further capture, the king MUST land on one of those squares - it cannot choose a "dead end" landing spot.

## Solution Design

Add a filtering step after collecting all potential landing squares for a king capture. Perform a "virtual" capture check that:
1. Considers the piece as if it were at the landing position
2. Temporarily treats the captured piece as removed (by passing it as an excluded position)
3. Checks all directions for potential enemy pieces to capture

## Implementation Steps

### Step 1: Add Helper Method `_has_capture_from_position()`

Add after line 200 in `board.py`:

```python
def _has_capture_from_position(
    self,
    pos: str,
    piece: Piece,
    excluded_positions: List[str]
) -> bool:
    """Check if piece at pos can capture, excluding given positions."""
    col, row = self.pos_to_coords(pos)
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    for dc, dr in directions:
        if piece.is_king():
            distance = 1
            found_enemy = False

            while True:
                check_col = col + (dc * distance)
                check_row = row + (dr * distance)
                check_pos = self.coords_to_pos(check_col, check_row)

                if not check_pos:
                    break

                if check_pos in excluded_positions:
                    distance += 1
                    continue

                check_piece = self.get_piece(check_pos)

                if not found_enemy:
                    if check_piece:
                        if check_piece.color != piece.color:
                            found_enemy = True
                        else:
                            break
                else:
                    if check_piece:
                        break
                    else:
                        return True

                distance += 1
        else:
            mid_col, mid_row = col + dc, row + dr
            mid_pos = self.coords_to_pos(mid_col, mid_row)

            if not mid_pos or mid_pos in excluded_positions:
                continue

            mid_piece = self.get_piece(mid_pos)
            if not mid_piece or mid_piece.color == piece.color:
                continue

            land_col, land_row = mid_col + dc, mid_row + dr
            land_pos = self.coords_to_pos(land_col, land_row)

            if land_pos:
                if land_pos in excluded_positions or not self.get_piece(land_pos):
                    return True

    return False
```

### Step 2: Modify King Capture Logic in `_get_single_captures()`

Replace the king capture section (lines 144-176) to collect moves first, then filter:

```python
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

    # Filter: keep only moves allowing chain capture if any exist
    if direction_captures:
        can_continue = []
        cannot_continue = []

        for move in direction_captures:
            has_further = self._has_capture_from_position(
                move.to_pos,
                piece,
                move.captured_positions or []
            )
            if has_further:
                can_continue.append(move)
            else:
                cannot_continue.append(move)

        if can_continue:
            captures.extend(can_continue)
        else:
            captures.extend(cannot_continue)
```

## Files Changed

- `bot/bl/board.py` - Add helper method and modify `_get_single_captures()`

## Testing Scenarios

1. King capture with chain opportunity - only chain-enabling landing spots offered
2. King capture with multiple chain opportunities - all chain-enabling spots offered
3. King capture with no chain opportunity - all landing spots offered
4. Regular piece capture - unchanged behavior
5. Chain capture in progress - filtering applies to subsequent captures

## Edge Cases Handled

- Captured piece excluded from path when checking further captures
- Multiple captures in different directions processed independently
- King at edge of board handled by coordinate bounds checking
