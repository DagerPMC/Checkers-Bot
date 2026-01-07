# Problem Statement

## Description
When a checkers game starts via inline query, the game's display language is not persisted. As two players with different language preferences interact with the game (making moves, viewing the board), the displayed language constantly switches between their preferred languages. This creates a confusing and inconsistent user experience.

## Expected Behavior
The game should maintain a single, consistent language throughout its lifecycle, from invitation to completion. The language should be determined when the game is created (based on the player who sent the invitation) and should remain the same regardless of which player is currently interacting with the game.

## Actual Behavior
The game's display language changes dynamically based on the `language_code` of whichever user is currently making a move or interacting with the game. This is because:

1. The i18n middleware (`TelegramI18nMiddleware`) determines locale based on `event_from_user` on every request
2. Each callback query (move, select piece, etc.) triggers the middleware to get the current user's language
3. When the message is updated with `edit_message_text()`, it uses the requesting user's language
4. No language preference is stored with the Game model in the database

Example scenario:
- Player A (Ukrainian language) creates game invitation
- Player B (English language) accepts
- Move 1 by Player A: Game displays in Ukrainian
- Move 2 by Player B: Game displays in English
- Move 3 by Player A: Game displays in Ukrainian
- And so on...

## Root Cause Analysis
The root cause is architectural:

1. **No game-level language persistence**: The `Game` model does not have a `language` or `locale` field
2. **Request-scoped localization**: The i18n middleware (`bot/middlewares/i18n.py`) resolves locale per-request based on the current user's Telegram language settings
3. **No context override**: When editing game messages, there's no mechanism to override the current user's language with the game's persisted language

The i18n middleware's `get_locale()` method:
```python
async def get_locale(self, event: TelegramObject, data: Dict[str, Any]) -> str:
    user: User | None = data.get("event_from_user")
    if user and user.language_code:
        lang = user.language_code.lower().split("-")[0]
        if lang in ["uk"]:
            return "uk"
        return "en"
    return self.i18n.default_locale
```

This always returns the current event user's language, with no consideration for game-level preferences.

## Affected Components

### Database Layer
- `/home/dager/projects/personal/checkers/bot/db/models/game.py` - Game model needs `locale` field

### Business Logic
- `/home/dager/projects/personal/checkers/bot/bl/game.py` - `create_game()` needs to save initial locale
- `/home/dager/projects/personal/checkers/bot/bl/game.py` - `accept_game()` and other game operations need to maintain locale

### Controllers
- `/home/dager/projects/personal/checkers/bot/controllers/inline.py` - Inline query handler (game creation)
- `/home/dager/projects/personal/checkers/bot/controllers/game.py` - All callback handlers that update game messages (accept, move, select, deselect, draw, surrender)
- `/home/dager/projects/personal/checkers/bot/controllers/history.py` - History viewer might also need locale from game

### Utilities
- `/home/dager/projects/personal/checkers/bot/utils/keyboard.py` - Keyboard generation uses `gettext()` which needs proper locale context
- `/home/dager/projects/personal/checkers/bot/middlewares/i18n.py` - May need extension to support game-level locale override

### Database Migration
- New Alembic migration needed to add `locale` column to `games` table

## Classification
**Complexity:** small

**Reason:**
While this affects multiple files, the solution is straightforward:
1. Add a single column (`locale`) to the Game model
2. Set it when the game is created (from white player's language)
3. Pass it through to the i18n context when rendering game messages
4. Update 2-3 controller methods to use game locale instead of user locale

The implementation requires:
- Database schema change (1 migration)
- Model update (1 field addition)
- Business logic update (1-2 functions to capture/use locale)
- Controller updates (modify existing message rendering to use game locale)
- Estimated total: 50-80 lines of code changes

This is NOT trivial (requires DB migration and understanding i18n flow), but it's also NOT medium because:
- No new architectural patterns needed
- No complex data flow changes
- Straightforward linear fix across a small number of files
- Well-defined scope with clear solution path
