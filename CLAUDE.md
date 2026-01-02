# Checkers Telegram Bot - Project Documentation

## Project Overview
A Telegram bot for playing checkers (draughts) with inline game invitations, real-time gameplay, and statistics tracking.

## Technology Stack
- **Python 3.13+**
- **aiogram 3.x** - Modern async Telegram bot framework
- **PostgreSQL** - Database for game state and statistics
- **SQLAlchemy 2.x** - ORM for database operations
- **Docker + docker-compose** - Containerization
- **asyncpg** - Async PostgreSQL driver

## Requirements

### 1. Game Invitation System
- User initiates game using Telegram inline functionality
- User can send invitation to any chat
- Invitation message includes:
  - Two inline buttons:
    - "Accept & Join Game" - joins the game
    - "Cancel Invitation" - cancels the invitation

### 2. Active Game Display
After invitation is accepted:
- Message updates to show game board
- Display information:
  - Two players and their colors (White/Black)
  - Current turn indicator
  - 8x8 checkers board using inline keyboard buttons

### 3. Board Representation
- Standard 8x8 checkers board
- Only playable squares (dark squares) are interactive
- Board elements:
  - **Empty playable squares**: dot emoji or button
  - **White pieces**: ⚪ (white circle emoji)
  - **Black pieces**: ⚫ (black circle emoji)
  - **White kings**: ⬜ (white square emoji)
  - **Black kings**: ⬛ (black square emoji)
- Interactive buttons for all valid moves

### 4. Game Rules - Standard Checkers
- 8x8 board, pieces move diagonally on dark squares
- Regular pieces move forward diagonally
- Capturing is mandatory when available
- Multiple captures in one turn (chain captures)
- Pieces are promoted to kings when reaching opposite end
- Kings can move diagonally in all directions
- Win conditions:
  - Capture all opponent pieces
  - Opponent has no legal moves
- Draw conditions (optional):
  - Mutual agreement
  - Repetition of position

### 5. Statistics Tracking
- Track per user:
  - Total games played
  - Wins
  - Losses
  - Win rate
- NO Elo system
- Simple gameplay and stats display

## Project Structure (Following memefinder pattern)

```
checkers/
├── bot/
│   ├── __init__.py
│   ├── __main__.py
│   ├── main.py              # Entry point
│   ├── config.py            # Configuration management
│   ├── controllers/         # Handlers for different bot actions
│   │   ├── __init__.py
│   │   ├── router.py        # Main router
│   │   ├── inline.py        # Inline query handler
│   │   ├── game.py          # Game logic handlers
│   │   └── stats.py         # Statistics handlers
│   ├── db/                  # Database models and session
│   │   ├── __init__.py
│   │   ├── session.py       # DB session management
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── user.py      # User model
│   │       ├── game.py      # Game model
│   │       └── move.py      # Move history model
│   ├── bl/                  # Business logic (game engine)
│   │   ├── __init__.py
│   │   ├── board.py         # Board representation
│   │   ├── piece.py         # Piece logic
│   │   ├── move.py          # Move generation and execution
│   │   ├── game.py          # Game business logic
│   │   └── user.py          # User business logic
│   ├── middlewares/         # Bot middlewares
│   │   ├── __init__.py
│   │   ├── user.py          # User middleware
│   │   └── session.py       # DB session middleware
│   └── utils/               # Utility functions
│       ├── __init__.py
│       ├── setup.py         # Initialization utilities
│       └── keyboard.py      # Inline keyboard generators
├── config/
│   └── local.yaml           # Local configuration
├── migrations/              # Alembic migrations
├── requirements/
│   ├── prod.txt            # Production dependencies
│   └── tools.txt           # Development dependencies
├── Dockerfile
├── docker-compose.yaml
├── alembic.ini
├── .dockerignore
├── .gitignore
└── CLAUDE.md               # This file
```

## Database Schema

### Users Table
```sql
- id (PK, BigInt) - Telegram user ID
- username (String, nullable)
- first_name (String)
- last_name (String, nullable)
- created_at (DateTime)
- total_games (Integer, default=0)
- wins (Integer, default=0)
- losses (Integer, default=0)
```

### Games Table
```sql
- id (PK, UUID)
- white_player_id (FK -> Users.id)
- black_player_id (FK -> Users.id)
- chat_id (BigInt)
- message_id (BigInt)
- board_state (JSON) - Current board representation
- current_turn (Enum: WHITE, BLACK)
- status (Enum: PENDING, ACTIVE, FINISHED, CANCELLED)
- winner_id (FK -> Users.id, nullable)
- created_at (DateTime)
- updated_at (DateTime)
- finished_at (DateTime, nullable)
```

### Moves Table (Optional - for move history)
```sql
- id (PK, Integer)
- game_id (FK -> Games.id)
- player_id (FK -> Users.id)
- from_position (String) - e.g., "a3"
- to_position (String) - e.g., "b4"
- captured_positions (JSON, nullable) - List of captured piece positions
- promoted (Boolean, default=False)
- move_number (Integer)
- created_at (DateTime)
```

## Board State Representation (JSON)
```json
{
  "squares": {
    "a1": null,
    "a3": {"color": "white", "king": false},
    "a5": {"color": "black", "king": false},
    "h8": {"color": "black", "king": true}
  },
  "must_capture": ["a3", "c3"]  // Pieces that must capture
}
```

## Key Features to Implement

1. **Inline Query Handler**
   - Respond to inline queries with "Start Checkers Game" option
   - Generate invitation message with inline buttons

2. **Callback Handlers**
   - Accept invitation → Create game, update message
   - Cancel invitation → Delete message or mark as cancelled
   - Move selection → Highlight possible moves
   - Execute move → Update board, switch turn

3. **Game Logic Engine**
   - Move validation
   - Capture detection (mandatory captures)
   - King promotion
   - Win/loss detection
   - Board rendering to inline keyboard

4. **Statistics System**
   - Update user stats on game completion
   - Display user stats on command

## Development Notes

### Docker Setup (from memefinder)
- Multi-stage Dockerfile (base, prod, dev)
- docker-compose with PostgreSQL service
- Hot reload with watchfiles in dev mode
- Volume mounting for local development

### Bot Configuration
- Support webhook and polling modes
- Configuration via YAML file
- Environment variables for secrets

### Middleware Pattern
- Session middleware for DB access
- User middleware for user management
- Include in update pipeline

### Inline Keyboard Best Practices
- Use callback_data with format: `action:game_id:data`
- Example: `move:uuid:a3-b4`, `accept:uuid`, `cancel:uuid`
- Keep callback_data under 64 bytes
- Use keyboard builders from aiogram

### Code Quality Standards
All code must adhere to PEP8 and pass local quality checks:

- **PEP8 Compliance**: Follow Python Enhancement Proposal 8 style guide
- **isort**: Import sorting configured in `.isort.cfg`
  - Line length: 80 characters
  - Multi-line output with trailing commas
  - Run: `docker compose run --rm --no-deps bot isort bot/`
- **flake8**: Code style linting configured in `.flake8`
  - Max line length: 80 characters
  - Ignores: E203, W503
  - Run: `docker compose run --rm --no-deps bot flake8 bot/`
- **mypy**: Static type checking configured in `mypy.ini`
  - Python version: 3.13
  - Strict type checking enabled
  - Run: `docker compose run --rm --no-deps bot mypy bot/`

All code must pass these checks before committing.

## Next Steps
1. Set up project structure (Dockerfile, docker-compose, requirements)
2. Initialize PostgreSQL with SQLAlchemy models
3. Set up Alembic migrations
4. Implement game logic engine
5. Create inline query and callback handlers
6. Build keyboard generators for board display
7. Implement statistics tracking
8. Testing and refinement

## Important Emoji Reference
- ⚪ White piece (U+26AA)
- ⚫ Black piece (U+26AB)
- ⬜ White king (U+2B1C)
- ⬛ Black king (U+2B1B)
- ⬝ Empty square option (U+2B1D) or • (U+2022)

## Reference Projects
- **memefinder** (`../memefinder`) - Telegram bot structure reference
- Uses aiogram 3.x, PostgreSQL, Docker setup
