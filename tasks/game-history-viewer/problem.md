# Problem Statement

## Summary
Users need the ability to view their previously played (finished) games and navigate through the move history, allowing them to replay games move-by-move to analyze their gameplay.

## Requirements

### Functional Requirements
- Extend inline query to show user's finished games as inline results
- Display game metadata: opponent name, game result (win/loss/draw), date played
- Selecting a game sends a message with the game viewer
- Display selected game with board state at specific move position
- Provide navigation controls to move forward/backward through move history
- Show current move number and total moves in the game
- Display player information and final game result
- Handle edge cases: no games played, games with no moves recorded

### User Flow
1. User triggers inline query (types @botname in any chat)
2. Bot shows inline results: "Start New Game" + list of finished games
3. User selects a finished game from the inline results
4. Bot sends message with game board at final position and navigation controls:
   - "⏮" (Jump to Start) button
   - "◀" (Previous Move) button
   - "▶" (Next Move) button
   - "⏭" (Jump to End) button
   - Current position indicator (e.g., "Move 5/24")
5. User navigates through moves using buttons
6. Board updates to show position at selected move

### Technical Considerations

#### Data Availability
- **Moves table exists** in database schema with: `game_id`, `player_id`, `from_position`, `to_position`, `captured_positions`, `promoted`, `move_number`
- **Critical issue**: Moves are NOT currently being saved during gameplay
  - `bot/controllers/game.py` executes moves but doesn't persist to database
  - Need to add Move record creation in `handle_move()` function
- **Games table** has all necessary metadata: players, winner, status, timestamps
- **Board state** stored as JSON in Game model but only current state (not historical)

#### Implementation Approach
1. **Fix move persistence**: Update `bot/controllers/game.py::handle_move()` to save Move records
2. **Extend inline handler**: Update `bot/controllers/inline.py` to include finished games
3. **New controller**: Create `bot/controllers/history.py` for game viewer callbacks
4. **Business logic**: Add functions in `bot/bl/game.py`:
   - `get_user_finished_games(user_id, limit)` - fetch finished games
   - `get_game_moves(game_id)` - fetch ordered move list
   - `reconstruct_board_at_move(game_id, move_number)` - rebuild board state
5. **Keyboard utility**: Add `create_history_keyboard()` in `bot/utils/keyboard.py`
6. **Board reconstruction**: Use existing `Board` class to replay moves from initial position

#### Callback Data Format
```
hv:{game_id}:{move_num}    # history view at move
hp:{game_id}:{move_num}    # history prev
hn:{game_id}:{move_num}    # history next
hs:{game_id}               # history start (jump to 0)
he:{game_id}               # history end (jump to last)
```
Note: Short prefixes to stay under 64 bytes with UUID game_id

#### Board Reconstruction Algorithm
```python
# Start with initial board
board = Board()  # default starting position

# Get all moves for game ordered by move_number
moves = get_game_moves(game_id)

# Replay moves up to target move_number
for move in moves[:move_number]:
    board_move = Move(
        from_pos=move.from_position,
        to_pos=move.to_position,
        # ... other fields
    )
    board.execute_move(board_move)

return board
```

#### Integration Points
- Add router to `bot/controllers/router.py`
- Add i18n strings to locales files
- Use existing middleware pipeline (session, user, i18n)
- Follow existing patterns from `stats.py` and `game.py`

#### Edge Cases
- User has no finished games: show friendly message
- Game has no moves (cancelled/abandoned): show initial board only
- Very long games (100+ moves): ensure pagination works
- Move navigation at boundaries: disable prev/next appropriately

## Classification
**Complexity:** medium

**Justification:**
- **Multiple files involved**: New controller file, updates to existing game controller, business logic additions, keyboard utilities
- **New components**: Game history viewer, move navigation system, board reconstruction logic
- **Data model changes**: Need to fix move persistence (currently broken)
- **Estimated lines of code**: 300-400 lines
  - Move persistence fix: ~20-30 lines
  - Business logic (game queries, board reconstruction): ~80-100 lines
  - Controller handlers (list games, view game, navigation): ~120-150 lines
  - Keyboard builders: ~40-50 lines
  - Localization strings: ~30-40 lines
- **Follows existing patterns** but introduces new UI flow (game viewer with navigation)
- **Not trivial/small**: Requires coordination between multiple layers and new interaction pattern
- **Not large**: Uses existing infrastructure, no new architecture or major refactoring needed

## Acceptance Criteria

### Must Have
- [ ] Moves are persisted to database during gameplay
- [ ] Finished games appear in inline query results
- [ ] User can select a game from inline results to view
- [ ] User can navigate forward through moves in chronological order
- [ ] User can navigate backward through moves
- [ ] Board display accurately reflects position at selected move number
- [ ] Navigation buttons work correctly at boundaries
- [ ] Current move indicator shows position (e.g., "Move 5/24")
- [ ] Game metadata displayed: players, result, date

### Should Have
- [ ] "Jump to Start" and "Jump to End" buttons for quick navigation
- [ ] Localized strings for all UI text
- [ ] Visual distinction between game viewer and active game (no move/surrender buttons)

### Nice to Have
- [ ] Filter games by result (wins/losses/draws)
- [ ] Show captured pieces at each position
- [ ] Highlight last move made on the board
- [ ] Search for games by opponent name

### Testing Checklist
- [ ] Create new game, make moves, finish game - verify moves saved to database
- [ ] Inline query shows finished games alongside "Start New Game"
- [ ] Navigate through full game from start to end
- [ ] Navigate backward from end to start
- [ ] Test with game that has captures and promotions
- [ ] Test with game that ended in draw
- [ ] Verify callback data stays under 64 bytes
- [ ] Test navigation in inline message context
