# Implementation Plan: Game History Viewer

## Overview

This plan implements a game history viewer feature that allows users to:
1. View their finished games via inline query
2. Select a finished game to see the final board position
3. Navigate through move history with buttons to see the board at any point in the game

**Critical prerequisite**: Moves are currently NOT being persisted during gameplay. This must be fixed first.

## Dependencies

```
Step 1 (Fix Move Persistence)
    ↓
Step 2 (Business Logic) → Step 3 (Board Reconstruction)
    ↓
Step 4 (History Keyboard)
    ↓
Step 5 (Extend Inline Handler)
    ↓
Step 6 (History Controller)
    ↓
Step 7 (Router Integration)
    ↓
Step 8 (Localization)
```

---

## Step 1: Fix Move Persistence in Game Controller

**File:** `bot/controllers/game.py`

**Location:** After `board.execute_move(move)` in `handle_move` function

**Note on chain captures:** Each jump in a chain capture is recorded as a separate move. This is correct behavior - when a player makes multiple captures in one turn, each capture click is a distinct action that advances `move_number`.

**Imports to add at top:**
```python
from sqlalchemy import func, select
from bot.db.models import Move as MoveModel
```

**Code to add after `board.execute_move(move)`:**
```python
# Count existing moves for this game
move_count_result = await s.session.execute(
    select(func.count(MoveModel.id)).where(MoveModel.game_id == game.id)
)
move_count = move_count_result.scalar() or 0

# Create move record
db_move = MoveModel(
    game_id=game.id,
    player_id=user.id,
    from_position=from_pos,
    to_position=to_pos,
    captured_positions=move.captured_positions if move.captured_positions else None,
    promoted=move.promoted,
    move_number=move_count + 1
)
s.session.add(db_move)
```

---

## Step 2: Add Business Logic for Game History Queries

**File:** `bot/bl/game.py`

**Import to add:**
```python
from sqlalchemy import desc
```

**Code to add:**
```python
async def get_finished_games_for_user(user_id: int, limit: int = 10) -> list[Game]:
    """Get finished games for a user, ordered by most recent."""
    result = await s.session.execute(
        select(Game)
        .options(
            selectinload(Game.white_player),
            selectinload(Game.black_player)
        )
        .where(
            Game.status == GameStatus.FINISHED,
            (Game.white_player_id == user_id) | (Game.black_player_id == user_id)
        )
        .order_by(desc(Game.finished_at))
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_game_with_moves(game_id: UUID) -> Game | None:
    """Get a game with all its moves loaded."""
    result = await s.session.execute(
        select(Game)
        .options(
            selectinload(Game.white_player),
            selectinload(Game.black_player),
            selectinload(Game.moves)
        )
        .where(Game.id == game_id)
    )
    game = result.scalar_one_or_none()
    if game and game.moves:
        game.moves = sorted(game.moves, key=lambda m: m.move_number)
    return game
```

---

## Step 3: Add Board Reconstruction Function

**File:** `bot/bl/history.py` (new file)

```python
from typing import TYPE_CHECKING

from bot.bl.board import Board
from bot.bl.move import Move, MoveType

if TYPE_CHECKING:
    from bot.db.models import Move as MoveModel


def reconstruct_board_at_move(moves: list['MoveModel'], target_move: int) -> Board:
    """Reconstruct board state at a specific move number (0 = initial)."""
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
```

---

## Step 4: Create History Keyboard Builder

**File:** `bot/utils/keyboard.py`

**Code to add:**
```python
def create_history_board_keyboard(
    board: Board,
    game_id: str,
    current_move: int,
    total_moves: int
) -> InlineKeyboardMarkup:
    """Create non-interactive board with navigation buttons."""
    builder = InlineKeyboardBuilder()

    # Build board display (non-interactive)
    for row in range(7, -1, -1):
        row_buttons = []
        for col in range(8):
            pos = Board.coords_to_pos(col, row)
            if not pos or pos not in board.squares:
                row_buttons.append(InlineKeyboardButton(text="  ", callback_data="noop"))
                continue
            piece = board.get_piece(pos)
            button_text = piece.to_emoji() if piece else "•"
            row_buttons.append(InlineKeyboardButton(text=button_text, callback_data="noop"))
        builder.row(*row_buttons)

    # Navigation row: ⏮ ◀ [5/24] ▶ ⏭
    nav_buttons = []

    # Jump to start
    nav_buttons.append(InlineKeyboardButton(
        text="⏮",
        callback_data=f"hv:{game_id}:0" if current_move > 0 else "noop"
    ))

    # Previous
    nav_buttons.append(InlineKeyboardButton(
        text="◀",
        callback_data=f"hv:{game_id}:{current_move - 1}" if current_move > 0 else "noop"
    ))

    # Counter
    nav_buttons.append(InlineKeyboardButton(
        text=f"{current_move}/{total_moves}",
        callback_data="noop"
    ))

    # Next
    nav_buttons.append(InlineKeyboardButton(
        text="▶",
        callback_data=f"hv:{game_id}:{current_move + 1}" if current_move < total_moves else "noop"
    ))

    # Jump to end
    nav_buttons.append(InlineKeyboardButton(
        text="⏭",
        callback_data=f"hv:{game_id}:{total_moves}" if current_move < total_moves else "noop"
    ))

    builder.row(*nav_buttons)
    return builder.as_markup()
```

---

## Step 5: Extend Inline Handler for Finished Games

**File:** `bot/controllers/inline.py`

Extend to query finished games and add them as inline results after "Start New Game".

**Key changes:**
- Add `user: User` parameter (injected by user middleware, already applied to all handlers)
- Query finished games with `get_finished_games_for_user(user.id)`
- Create InlineQueryResultArticle for each finished game
- Each finished game result has callback button: `hview:{game_id}`

**Imports to add:**
```python
from bot.bl.game import get_finished_games_for_user
from bot.db.models import User
```

**Handler signature change:**
```python
async def handle_inline_query(query: InlineQuery, user: User) -> None:
```

---

## Step 6: Create History Controller

**File:** `bot/controllers/history.py` (new file)

**Handlers:**
1. `@router.callback_query(F.data.startswith("hview:"))` - Initial view (final position)
2. `@router.callback_query(F.data.startswith("hv:"))` - Navigate to specific move

**Callback data format:**
- `hview:uuid` - View game history (shows final position)
- `hv:uuid:5` - Navigate to move 5

**Authorization check (required in both handlers):**
```python
# Verify user was a participant in this game
if user.id not in [game.white_player_id, game.black_player_id]:
    await callback.answer(_('notif-not-in-game'))
    return
```

**Key logic:**
- Use `get_game_with_moves()` to load game with all moves
- Use `reconstruct_board_at_move()` to build board at target position
- Use `create_history_board_keyboard()` for display with navigation
- Handle both inline messages and regular messages (use helper function)

---

## Step 7: Register History Router

**File:** `bot/controllers/router.py`

```python
from bot.controllers.history import router as history_router
router.include_router(history_router)
```

---

## Step 8: Add Localization Strings

**Files:** `locales/en/LC_MESSAGES/messages.po`, `locales/uk/LC_MESSAGES/messages.po`

**Strings needed:**
- `history-title` - Inline result title (e.g., "View game vs {opponent}")
- `history-description` - Inline result description (e.g., "{result} - {date}")
- `history-message` - Message content when selected
- `history-result-won/lost/draw` - Result labels
- `btn-view-history` - View button text
- `history-header` - Message header
- `history-winner-white/black` - Winner text
- `history-ended-draw` - Draw text
- `history-initial-position` - Initial position label
- `history-after-white-move/black-move` - Turn indicators
- `notif-not-in-game` - Authorization error notification

After editing .po files, compile with msgfmt.

---

## Testing Checklist

- [ ] Move persistence: Play game, verify moves in database
- [ ] Board reconstruction: Verify correct state at each move
- [ ] Inline query: Finished games appear in results
- [ ] History view: Select game, see final position
- [ ] Navigation forward: Move 0 → final step by step
- [ ] Navigation backward: Final → move 0 step by step
- [ ] Jump buttons: First/last work correctly
- [ ] Edge case: Game with 0 moves shows initial position
- [ ] Authorization: Cannot view others' games
- [ ] Localization: EN and UK work correctly
