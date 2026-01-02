from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from bot.bl.board import Board
from bot.db.models import Game
from bot.db.models.game import GameStatus
from bot.db.session import s


async def create_game(
    white_player_id: int,
    chat_id: int,
    message_id: int
) -> Game:
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
