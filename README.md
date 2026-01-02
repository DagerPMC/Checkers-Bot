# Checkers Telegram Bot

A Telegram bot for playing checkers with inline game invitations, real-time gameplay, and statistics tracking.

## Features

- 🎮 Inline game invitations
- ♟️ Full checkers gameplay with standard rules
- 👑 Piece promotion to kings
- 📊 Player statistics tracking
- 🎯 Interactive board using Telegram inline keyboards

## Tech Stack

- Python 3.13+
- aiogram 3.x - Telegram bot framework
- PostgreSQL - Database
- SQLAlchemy 2.x - ORM
- Docker & docker-compose

## Setup

### 1. Prerequisites

- Docker and docker-compose installed
- Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))

### 2. Configuration

Copy the example config and add your bot token:

```bash
cp config/example.yaml config/local.yaml
```

Edit `config/local.yaml`:

```yaml
token: "YOUR_BOT_TOKEN_HERE"
updates_strategy: "polling"  # or "webhook"
database_dns: "postgresql+asyncpg://admin:admin@postgres:5432/checkers"
host_url: null  # Set this if using webhook mode
```

### 3. Run with Docker

Build and start the services:

```bash
docker-compose up --build
```

The bot will automatically:
- Start the PostgreSQL database
- Run database migrations
- Start the bot in polling mode

### 4. Initialize Database

Create the initial migration:

```bash
docker-compose exec bot alembic revision --autogenerate -m "Initial migration"
docker-compose exec bot alembic upgrade head
```

## Usage

### Starting a Game

1. In any chat, type `@your_bot_username`
2. Select "Start Checkers Game"
3. Send to the chat
4. Wait for someone to accept the invitation

### Playing

- Tap a piece to select it
- Green circles show valid moves
- Tap a destination to move
- Captures are mandatory!
- Reach the opposite end to promote to King

### Commands

- `/start` - Welcome message and instructions
- `/stats` - View your game statistics
- `/help` - Show game rules and help

## Game Rules

- Standard 8x8 checkers board
- Pieces move diagonally on dark squares
- Regular pieces move forward only
- Kings can move in all diagonal directions
- Captures are mandatory when available
- Multiple captures in one turn (chain captures)
- Win by capturing all opponent pieces or blocking all moves

## Development

### Project Structure

```
checkers/
├── bot/
│   ├── bl/              # Business logic
│   ├── controllers/     # Route handlers
│   ├── db/              # Database models
│   ├── game_logic/      # Checkers game engine
│   ├── middlewares/     # Bot middlewares
│   ├── utils/           # Utility functions
│   └── main.py          # Entry point
├── config/              # Configuration files
├── migrations/          # Alembic migrations
├── requirements/        # Python dependencies
├── Dockerfile
└── docker-compose.yaml
```

### Running Locally (without Docker)

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements/prod.txt
pip install -r requirements/tools.txt
```

3. Set up PostgreSQL and update `config/local.yaml`

4. Run migrations:
```bash
alembic upgrade head
```

5. Start the bot:
```bash
python -m bot.main
```

### Creating Migrations

After modifying database models:

```bash
docker-compose exec bot alembic revision --autogenerate -m "Description of changes"
docker-compose exec bot alembic upgrade head
```

## Environment Variables

- `CONFIG` - Path to configuration file (default: `./config/local.yaml`)

## Database Schema

### Users
- User information and statistics
- Total games, wins, losses

### Games
- Active and completed games
- Board state stored as JSON
- Current turn tracking
- Game status (pending, active, finished, cancelled)

### Moves
- Move history for each game
- Captured pieces tracking
- Promotion tracking

## Troubleshooting

### Bot not responding
- Check that the bot token is correct
- Verify the bot is running: `docker-compose ps`
- Check logs: `docker-compose logs -f bot`

### Database connection errors
- Ensure PostgreSQL is running: `docker-compose ps postgres`
- Check database DNS in config file
- Verify migrations are applied: `docker-compose exec bot alembic current`

### Inline mode not working
- Enable inline mode in @BotFather settings
- Send `/setinline` to @BotFather
- Set inline placeholder text

## License

MIT

## Credits

Built with aiogram 3.x and PostgreSQL.
