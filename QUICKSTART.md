# Quick Start Guide

## 1. Get Your Bot Token

1. Talk to [@BotFather](https://t.me/BotFather) on Telegram
2. Create a new bot with `/newbot`
3. Copy the token

## 2. Enable Inline Mode

1. Talk to [@BotFather](https://t.me/BotFather)
2. Use `/setinline` command
3. Select your bot
4. Set a placeholder like "Type to search games..."

## 3. Configure the Bot

Create your local configuration file:

```bash
cp config/example.yaml config/local.yaml
```

Edit `config/local.yaml` and add your bot token:

```yaml
token: "YOUR_BOT_TOKEN_HERE"
updates_strategy: "polling"
database_dns: "postgresql+asyncpg://admin:admin@postgres:5432/checkers"
host_url: null
```

## 4. Start the Bot

```bash
docker-compose up --build
```

Wait for the services to start (about 30-60 seconds).

## 5. Create Database Tables

In a new terminal:

```bash
# Create initial migration
docker-compose exec bot alembic revision --autogenerate -m "Initial tables"

# Apply migration
docker-compose exec bot alembic upgrade head
```

## 6. Test the Bot

1. Open Telegram
2. Start a chat with your bot or go to any chat
3. Type `@your_bot_username` (replace with your actual bot username)
4. Select "Start Checkers Game"
5. Send to chat
6. Click "Accept & Join"
7. Get a friend to click "Accept & Join" to start playing!

## Common Commands

```bash
# View logs
docker-compose logs -f bot

# Stop the bot
docker-compose down

# Restart the bot
docker-compose restart bot

# Access PostgreSQL
docker-compose exec postgres psql -U admin -d checkers

# Run alembic commands
docker-compose exec bot alembic upgrade head
docker-compose exec bot alembic revision --autogenerate -m "description"
```

## Troubleshooting

### Bot doesn't respond to inline queries
- Make sure you enabled inline mode in BotFather (`/setinline`)
- Check bot logs: `docker-compose logs -f bot`

### Database errors
- Make sure migrations are applied: `docker-compose exec bot alembic upgrade head`
- Check if PostgreSQL is running: `docker-compose ps postgres`

### "Can't play against yourself" error
- This is expected! You need two different Telegram accounts to test multiplayer
- Use Telegram Web on one device and Telegram app on another

## Development Mode

For development with auto-reload:

```bash
# Already configured in docker-compose.yaml
docker-compose up
```

The bot will automatically reload when you change Python files.

## Next Steps

- Read the full [README.md](README.md) for more details
- Check [CLAUDE.md](CLAUDE.md) for technical documentation
- Customize emoji and messages in `bot/controllers/`
- Extend game rules in `bot/game_logic/`

Have fun playing checkers! 🎮
