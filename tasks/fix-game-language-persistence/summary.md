# Fix Game Language Persistence - Summary

## Problem
When two players with different language preferences played a game, the displayed language constantly switched based on whose turn it was. This happened because the i18n middleware determined locale per-request from the current user's Telegram settings.

## Solution
Added a `locale` field to the Game model that captures and persists the inviting player's language when the game is created. All game-related messages now use this persisted locale instead of the current user's locale.

## Changes Made

### Database Layer
- **bot/db/models/game.py**: Added `locale: Mapped[str]` field with default `'en'`
- **migrations/versions/37902166f8c9_add_locale_to_games.py**: New migration adding `locale` column with `server_default='en'`

### Business Logic
- **bot/bl/game.py**: Updated `create_game()` to accept `locale` parameter

### i18n
- **bot/middlewares/i18n.py**: Added `gettext_with_locale(singular, locale, **kwargs)` function for locale-specific translations

### Keyboards
- **bot/utils/keyboard.py**:
  - Updated `create_invitation_keyboard()` to accept `locale` parameter
  - Updated `create_board_keyboard()` to accept `locale` parameter

### Controllers
- **bot/controllers/game.py**:
  - Added `get_user_locale()` helper function
  - All game handlers now use `game.locale` with `gettext_with_locale()` for translations
  - All keyboard function calls pass `locale=game.locale`

- **bot/controllers/history.py**:
  - All history handlers now use `game.locale` with `gettext_with_locale()` for translations

## How It Works
1. When a user creates a game (clicks "Accept & Join" on a fresh invitation), their Telegram `language_code` is captured
2. The locale is stored in the Game record in the database
3. All subsequent game message updates use this persisted locale via `gettext_with_locale()`
4. Both players see the game in the inviting player's language throughout the entire game

## Quality Checks
- isort: PASS
- flake8: PASS
- mypy: PASS (no issues in 34 source files)
