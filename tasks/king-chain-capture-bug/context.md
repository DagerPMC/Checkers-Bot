# Context: King Chain Capture Bug

## Problem Summary
When a king captures a piece, it has multiple possible landing squares (any empty square after the captured piece). If any of those landing squares would allow another capture, the king MUST land on one of those squares. Currently, the game allows landing on ANY empty square, even if it means abandoning a possible chain capture.

## The Rule
In checkers, when a king captures:
1. After jumping over an enemy piece, the king can land on any empty square along that diagonal
2. BUT if landing on square A allows another capture while landing on square B doesn't, the king MUST land on square A
3. If multiple landing squares allow further captures, the player can choose any of them

## Current Broken Behavior
The `_get_single_captures()` method (lines 144-176) adds ALL empty squares after a captured piece as valid landing spots without checking if further captures would be available from each spot.

## Key Files

### Core Logic - `bot/bl/board.py`
- `_get_single_captures()` (lines 137-200) - **THE BUG IS HERE**
  - For kings (lines 144-176): Adds all empty squares after captured piece as landing options
  - Does NOT check if further captures are available from each landing square
  - Should filter landing squares to only those allowing chain captures (if any exist)

- `get_valid_moves()` (lines 78-90) - Returns valid moves, calls `_get_single_captures`
- `execute_move()` (lines 212-223) - Executes a move, removes captured pieces

### Game Controller - `bot/controllers/game.py`
- `handle_move()` (lines 274-402) - Move execution
- Lines 316-322: Chain capture detection (checks AFTER landing, but the bug is in WHICH squares are offered)

### UI Layer - `bot/utils/keyboard.py`
- Lines 62-64: Shows green circles for valid move destinations

## Example of the Bug

```
Board state:
   a b c d e f g h
8  . . . . . . . .
7  . . . . . . . .
6  . . . ⚫ . . . .   <- enemy at d6
5  . . . . . . . .
4  . . . . . . . .
3  . . . ⚫ . . . .   <- enemy at c3
2  . ⬜ . . . . . .   <- white king at b2
1  . . . . . . . .

King at b2 captures d6's piece. Current behavior allows landing on:
- e7 (no further captures available)
- f8 (no further captures available)

But actually the king should NOT be able to land on e7 or f8 because
after capturing d6, landing at e5 would allow capturing c3 next!
The king MUST land on e5 (the square that enables the chain capture).
```

## The Fix Required

Modify `_get_single_captures()` for kings to:
1. Find all potential landing squares after jumping over an enemy piece
2. For each landing square, check if further captures would be available
3. If ANY landing squares have further captures available:
   - Only return those squares as valid moves
   - Filter out squares that don't allow continuation
4. If NO landing squares have further captures, return all of them (chain ends)

## Implementation Approach

In `_get_single_captures()`, after collecting all landing squares for a king capture:
1. Create a temporary board state for each potential landing
2. Check `_get_single_captures()` recursively from that position
3. Separate landing squares into "can continue" and "cannot continue"
4. If "can continue" is not empty, use only those; otherwise use all

Alternative simpler approach:
- Check each landing square without modifying board state
- Just look for enemy pieces diagonally from each landing square with empty squares behind them
