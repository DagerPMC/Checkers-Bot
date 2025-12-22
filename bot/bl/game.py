from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from bot.db.models import Game, User
from bot.db.models.game import GameStatus, PlayerColor
from bot.db.session import s
from bot.game_logic.board import Board


async def create_game(
    white_player_id: int,
    chat_id: int,
    message_id: int
) -> Game:
    """Create a new game."""
    board = Board()

    game = Game(
        white_player_id=white_player_id,
        chat_id=chat_id,
        message_id=message_id,
        board_state=board.to_dict(),
        status=GameStatus.PENDING
    )
    s.session.add(game)
    await s.session.flush()

    # Refresh to load relationships
    await s.session.refresh(game, ['white_player'])

    return game


async def accept_game(game_id: UUID, black_player_id: int) -> Game | None:
    """Accept a game invitation."""
    # Get game with relationships loaded
    result = await s.session.execute(
        select(Game)
        .options(selectinload(Game.white_player), selectinload(Game.black_player))
        .where(Game.id == game_id)
    )
    game = result.scalar_one_or_none()

    if not game or game.status != GameStatus.PENDING:
        return None

    game.black_player_id = black_player_id
    game.status = GameStatus.ACTIVE
    await s.session.flush()

    # Refresh to load the black_player relationship
    await s.session.refresh(game, ['black_player'])

    return game


async def cancel_game(game_id: UUID) -> bool:
    """Cancel a game invitation."""
    result = await s.session.execute(
        select(Game).where(Game.id == game_id)
    )
    game = result.scalar_one_or_none()

    if not game:
        return False

    game.status = GameStatus.CANCELLED
    await s.session.flush()

    return True


async def get_game(game_id: UUID) -> Game | None:
    """Get game by ID with eagerly loaded relationships."""
    result = await s.session.execute(
        select(Game)
        .options(selectinload(Game.white_player), selectinload(Game.black_player))
        .where(Game.id == game_id)
    )
    return result.scalar_one_or_none()


async def finish_game(game_id: UUID, winner_id: int | None) -> Game | None:
    """Finish a game and update statistics. winner_id=None means draw."""
    result = await s.session.execute(
        select(Game)
        .options(selectinload(Game.white_player), selectinload(Game.black_player))
        .where(Game.id == game_id)
    )
    game = result.scalar_one_or_none()

    if not game or game.status != GameStatus.ACTIVE:
        return None

    game.status = GameStatus.FINISHED
    game.winner_id = winner_id
    game.finished_at = datetime.utcnow()

    # Update user statistics - they're already loaded via selectinload
    white_player = game.white_player
    black_player = game.black_player

    if white_player and black_player:
        white_player.total_games += 1
        black_player.total_games += 1

        if winner_id == white_player.id:
            white_player.wins += 1
            black_player.losses += 1
        elif winner_id == black_player.id:
            black_player.wins += 1
            white_player.losses += 1
        # If winner_id is None, it's a draw - no wins/losses updated

    await s.session.flush()

    return game
