# Plan Review

## Verdict: PLAN APPROVED (after revision)

## Strengths

1. **Correct identification of the critical prerequisite**: Moves not being persisted is correctly prioritized first
2. **Good step dependency ordering**: Clear dependency diagram with correct order
3. **Proper use of SQLAlchemy patterns**: Uses `selectinload` consistent with existing code
4. **Appropriate callback data format**: `hv:{game_id}:{move_number}` follows existing patterns
5. **Complete testing checklist**: Comprehensive scenarios including edge cases

## Issues

### Issue 1: Incomplete Move Persistence Logic
**Severity:** Critical
**Description:** The plan doesn't account for chain captures properly. Each segment of a chain capture could be recorded separately OR aggregated into one move.

**Recommendation:** Record each jump in a chain capture as a separate move (each with incrementing `move_number`). This is actually the correct behavior - each click that captures a piece IS a separate move.

### Issue 2: Missing Authorization Check
**Severity:** Major
**Description:** Step 6 (History Controller) needs explicit authorization to verify user was a game participant.

**Recommendation:** Add check: `if user.id not in [game.white_player_id, game.black_player_id]: return error`

### Issue 3: Inline Query User Access
**Severity:** Major
**Description:** Current inline handler doesn't receive `user` parameter. Need to clarify how to get user context.

**Recommendation:** Use `query.from_user.id` directly to query finished games, since the user middleware should already be applied.

### Issue 4: Missing Import Statements
**Severity:** Minor
**Description:** Some imports not shown (e.g., `desc()` in Step 2)

**Recommendation:** Include complete imports in code blocks

## Resolution

All issues are addressable. The chain capture behavior (recording each jump separately) is actually correct since that's how the game works - each capture click is a distinct move.
