from bot.db.models import User
from bot.db.session import s


async def create_or_update_user(
    id: int,
    username: str | None,
    first_name: str,
    last_name: str | None,
) -> User:
    if not (user := await s.session.get(User, id)):
        user = User(id=id)
        s.session.add(user)

    user.username = username
    user.first_name = first_name
    user.last_name = last_name

    await s.session.flush()

    return user


async def get_user_stats(user_id: int) -> dict:
    user = await s.session.get(User, user_id)
    if not user:
        return {
            "total_games": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0
        }

    win_rate = (
        (user.wins / user.total_games * 100)
        if user.total_games > 0
        else 0.0
    )

    return {
        "total_games": user.total_games,
        "wins": user.wins,
        "losses": user.losses,
        "win_rate": win_rate
    }
