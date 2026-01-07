# Checkers Telegram Bot

Telegram bot for playing checkers (draughts) with inline game invitations, real-time gameplay, and statistics tracking.

### Slash Commands

| Command | Description |
|---------|-------------|
| `/workflow [task]` | Full 7-phase workflow (problem → plan → implement → review → verify) |
| `/plan [task]` | Create implementation plan using Planner subagent (opus) |
| `/review-plan [plan.md]` | Review plan using Plan-Reviewer subagent (opus) |
| `/gather-context [topic]` | Find 10-20 relevant files for a topic |
| `/simplify [file\|staged]` | Simplify code using Code-Simplifier subagent |
| `/review-code [file\|staged]` | Review code for bugs/vulnerabilities (opus) |
| `/verify [problem]` | Verify implementation solves the problem |

### Workflow Phases
1. Problem clarification (requires approval)
2. Context gathering
3. Planning with subagent review (requires approval)
4. Implementation
5. Code quality review
6. Verification and testing

### Subagent Prompts
Detailed prompts for each subagent are in `AGENTS.md` under "Subagent Specifications" section

---

## Tech Stack

- Python 3.13, aiogram 3.x
- PostgreSQL, SQLAlchemy 2.x (async), Alembic
- Docker + docker-compose
- Key packages: `asyncpg`, `pydantic`

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

---

## Directory Structure

```
checkers/
├── bot/                     # Main application
│   ├── main.py              # Entry point
│   ├── config.py            # Configuration management
│   ├── controllers/         # API handlers
│   │   ├── router.py        # Router composition
│   │   ├── inline.py        # Inline query handler
│   │   ├── game.py          # Game logic handlers
│   │   └── stats.py         # Statistics handlers
│   ├── db/                  # Database layer
│   │   ├── session.py       # Session management
│   │   └── models/          # SQLAlchemy models (User, Game, Move)
│   ├── bl/                  # Business logic
│   │   ├── board.py         # Board representation
│   │   ├── piece.py         # Piece logic
│   │   ├── move.py          # Move validation & execution
│   │   ├── game.py          # Game engine
│   │   └── user.py          # User logic
│   ├── middlewares/         # Request processing
│   │   ├── user.py          # User middleware
│   │   └── session.py       # DB session middleware
│   └── utils/               # Utilities
│       ├── setup.py         # Initialization
│       └── keyboard.py      # Keyboard generators
├── config/
│   └── local.yaml           # Local configuration
├── migrations/              # Alembic migrations
├── requirements/
│   ├── prod.txt             # Production dependencies
│   └── tools.txt            # Development tools
├── Dockerfile
├── docker-compose.yaml
└── alembic.ini
```

---

## Database Schema

**Users** (Telegram user data & statistics)
- `id` (PK, BigInt) - Telegram user ID
- `username`, `first_name`, `last_name`
- `total_games`, `wins`, `losses`
- `created_at`

**Games** (Game state & metadata)
- `id` (PK, UUID)
- `white_player_id`, `black_player_id` (FK -> Users)
- `chat_id`, `message_id` (BigInt)
- `board_state` (JSON) - Board representation
- `current_turn` (Enum: WHITE, BLACK)
- `status` (Enum: PENDING, ACTIVE, FINISHED, CANCELLED)
- `winner_id` (FK -> Users, nullable)
- `created_at`, `updated_at`, `finished_at`

**Moves** (Move history, optional)
- `id` (PK, Integer)
- `game_id` (FK -> Games), `player_id` (FK -> Users)
- `from_position`, `to_position` (e.g., "a3", "b4")
- `captured_positions` (JSON) - Captured pieces
- `promoted` (Boolean), `move_number`
- `created_at`

### Board State Format
```json
{
  "squares": {
    "a1": null,
    "a3": {"color": "white", "king": false},
    "a5": {"color": "black", "king": false},
    "h8": {"color": "black", "king": true}
  },
  "must_capture": ["a3", "c3"]
}
```

---

## Key Features

1. **Inline Query Handler** - Respond with "Start Checkers Game", generate invitation message
2. **Callback Handlers** - Accept/cancel invitation, move selection, execute moves
3. **Game Logic Engine** - Move validation, capture detection, king promotion, win/loss detection
4. **Statistics System** - Track and display user stats
5. **Board Rendering** - Convert game state to inline keyboard

---

## Commands

```bash
# Setup (development)
docker-compose up -d              # Start PostgreSQL
python -m venv venv && source venv/bin/activate
pip install -r requirements/prod.txt -r requirements/tools.txt

# Database
alembic upgrade head              # Run migrations
alembic revision --autogenerate -m "description"

# Run bot
python -m bot                     # Polling mode
python -m bot --webhook           # Webhook mode

# Code Quality
isort bot/                        # Import sorting
flake8 bot/                       # Linting
mypy bot/                         # Type checking

# Docker
docker-compose run --rm --no-deps bot isort bot/
docker-compose run --rm --no-deps bot flake8 bot/
docker-compose run --rm --no-deps bot mypy bot/
```

---

## Implementation Notes

### Callback Data Format
```
action:game_id:data
move:uuid:a3-b4
accept:uuid
cancel:uuid
```
Keep under 64 bytes, use aiogram keyboard builders

### Configuration
- Polling/webhook modes via YAML
- Environment variables for secrets
- Multi-stage Docker (base, prod, dev)

### Middleware Pipeline
- Session middleware (DB access)
- User middleware (user management)

---

## Code Style

- Python 3.13 with type hints
- 80 char line length, 4 spaces indentation
- PEP8 compliance (isort, flake8, mypy)
- Self-documenting code - avoid unnecessary comments
- Async/await patterns throughout

### Quality Checks (`.isort.cfg`, `.flake8`, `mypy.ini`)
- **isort**: Import sorting, multi-line with trailing commas
- **flake8**: Max line 80, ignores E203/W503
- **mypy**: Strict type checking, Python 3.13

All code must pass quality checks before committing.

---

## Game Elements

### Board Emojis
- ⚪ White piece (U+26AA)
- ⚫ Black piece (U+26AB)
- ⬜ White king (U+2B1C)
- ⬛ Black king (U+2B1B)
- ⬝ Empty square (U+2B1D) or • (U+2022)

### Standard Rules
- 8x8 board, diagonal movement on dark squares
- Regular pieces move forward, kings move all directions
- Mandatory captures, chain captures allowed
- Promotion to king at opposite end
- Win: capture all pieces or block all moves

---

## Important Notes

- Follow aiogram 3.x async patterns
- Use SQLAlchemy async sessions
- Keep callback_data under 64 bytes
- Follow existing middleware pipeline pattern
- Reference `../memefinder` for bot structure patterns
- Use keyboard builders for inline keyboards
- Mock external dependencies in tests
- Do not create context.md
- DO NOT WRITE DOCSTRINGS AND COMMENTS