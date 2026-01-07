from datetime import datetime
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.orm import selectinload

from bot.bl.board import Board
from bot.db.models import Game
from bot.db.models.game import GameStatus
from bot.db.session import s


async def create_game(
    white_player_id: int,
    chat_id: int,
    message_id: int,
    locale: str = 'en'
) -> Game:
    board = Board()

    game = Game(
        white_player_id=white_player_id,
        chat_id=chat_id,
        message_id=message_id,
        board_state=board.to_dict(),
        status=GameStatus.PENDING,
        locale=locale
    )
    s.session.add(game)
    await s.session.flush()

    await s.session.refresh(game, ['white_player'])

    return game


async def accept_game(game_id: UUID, black_player_id: int) -> Game | None:
    result = await s.session.execute(
        select(Game)
        .options(
            selectinload(Game.white_player),
            selectinload(Game.black_player)
        )
        .where(Game.id == game_id)
    )
    game = result.scalar_one_or_none()

    if not game or game.status != GameStatus.PENDING:
        return None

    game.black_player_id = black_player_id
    game.status = GameStatus.ACTIVE
    await s.session.flush()

    await s.session.refresh(game, ['black_player'])

    return game


async def cancel_game(game_id: UUID) -> bool:
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
    result = await s.session.execute(
        select(Game)
        .options(
            selectinload(Game.white_player),
            selectinload(Game.black_player)
        )
        .where(Game.id == game_id)
    )
    return result.scalar_one_or_none()


async def finish_game(game_id: UUID, winner_id: int | None) -> Game | None:
    result = await s.session.execute(
        select(Game)
        .options(
            selectinload(Game.white_player),
            selectinload(Game.black_player)
        )
        .where(Game.id == game_id)
    )
    game = result.scalar_one_or_none()

    if not game or game.status != GameStatus.ACTIVE:
        return None

    game.status = GameStatus.FINISHED
    game.winner_id = winner_id
    game.finished_at = datetime.utcnow()

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

    await s.session.flush()

    return game


async def get_finished_games_for_user(
    user_id: int,
    limit: int = 10
) -> list[Game]:
    """Get finished games for a user, ordered by most recent."""
    result = await s.session.execute(
        select(Game)
        .options(
            selectinload(Game.white_player),
            selectinload(Game.black_player)
        )
        .where(
            Game.status == GameStatus.FINISHED,
            (Game.white_player_id == user_id)
            | (Game.black_player_id == user_id)
        )
        .order_by(desc(Game.finished_at))
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_game_with_moves(game_id: UUID) -> Game | None:
    """Get a game with all its moves loaded, ordered by move number."""
    result = await s.session.execute(
        select(Game)
        .options(
            selectinload(Game.white_player),
            selectinload(Game.black_player),
            selectinload(Game.moves)
        )
        .where(Game.id == game_id)
    )
    game = result.scalar_one_or_none()

    if game and game.moves:
        game.moves = sorted(game.moves, key=lambda m: m.move_number)

    return game
