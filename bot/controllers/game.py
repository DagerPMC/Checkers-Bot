from uuid import UUID

from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    ChosenInlineResult,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.bl.board import Board
from bot.bl.game import (
    accept_game,
    cancel_game,
    create_game,
    finish_game,
    get_game,
)
from bot.bl.piece import PieceColor
from bot.db.models import User
from bot.db.models.game import GameStatus, PlayerColor
from bot.utils.keyboard import create_board_keyboard, create_invitation_keyboard

router = Router()


async def edit_game_message(
    callback: CallbackQuery,
    text: str,
    keyboard=None
) -> None:
    if callback.message and hasattr(callback.message, 'edit_text'):
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    elif callback.inline_message_id and callback.bot:
        await callback.bot.edit_message_text(
            text=text,
            inline_message_id=callback.inline_message_id,
            parse_mode="HTML",
            reply_markup=keyboard
        )


@router.chosen_inline_result()
async def handle_chosen_inline_result(
    result: ChosenInlineResult, user: User
) -> None:
    if (
        result.result_id == "checkers_invite"
        and result.inline_message_id
    ):
        pass


@router.callback_query(F.data.startswith("accept:"))
async def handle_accept_game(callback: CallbackQuery, user: User) -> None:
    if not callback.data:
        await callback.answer("Invalid request")
        return
    game_id_str = callback.data.split(":")[1]

    if callback.message:
        chat_id = callback.message.chat.id
        message_id = callback.message.message_id
    elif callback.inline_message_id:
        chat_id = 0
        message_id = 0
    else:
        await callback.answer("Error: Could not identify message")
        return

    if game_id_str == "new":
        game = await create_game(
            white_player_id=user.id,
            chat_id=chat_id,
            message_id=message_id
        )

        text = (f"🎮 <b>Checkers Game</b>\n\n"
                f"⚪ White: {user.first_name}\n"
                f"⚫ Black: <i>waiting...</i>\n\n"
                f"Waiting for opponent to join...")

        keyboard = create_invitation_keyboard(str(game.id))
        await edit_game_message(callback, text, keyboard)
        await callback.answer("Game created! Waiting for opponent...")
        return

    try:
        game_id = UUID(game_id_str)
    except ValueError:
        await callback.answer("Invalid game ID")
        return

    maybe_game = await get_game(game_id)
    if not maybe_game:
        await callback.answer("Game not found")
        return

    game = maybe_game
    if game.white_player_id == user.id:
        await callback.answer("You can't play against yourself!")
        return

    accepted_game = await accept_game(game_id, user.id)

    if not accepted_game:
        await callback.answer("Game already started or not available")
        return

    board = Board.from_dict(accepted_game.board_state)

    white_name = accepted_game.white_player.first_name
    black_name = (
        accepted_game.black_player.first_name
        if accepted_game.black_player
        else "Unknown"
    )

    text = (f"🎮 <b>Checkers Game</b>\n\n"
            f"⚪ White: {white_name}\n"
            f"⚫ Black: {black_name}\n\n"
            f"Current turn: ⚪ White")

    keyboard = create_board_keyboard(
        board, str(accepted_game.id), PieceColor.WHITE
    )
    await edit_game_message(callback, text, keyboard)
    await callback.answer("Game started! White moves first.")


@router.callback_query(F.data.startswith("cancel:"))
async def handle_cancel_game(callback: CallbackQuery, user: User) -> None:
    if not callback.data:
        await callback.answer("Invalid request")
        return
    game_id_str = callback.data.split(":")[1]

    if game_id_str == "new":
        await edit_game_message(callback, "❌ Game invitation cancelled.")
        await callback.answer("Game cancelled")
        return

    try:
        game_id = UUID(game_id_str)
    except ValueError:
        await callback.answer("Invalid game ID")
        return

    success = await cancel_game(game_id)

    if success:
        await edit_game_message(callback, "❌ Game invitation cancelled.")
        await callback.answer("Game cancelled")
    else:
        await callback.answer("Failed to cancel game")


@router.callback_query(F.data.startswith("select:"))
async def handle_select_piece(callback: CallbackQuery, user: User) -> None:
    if not callback.data:
        await callback.answer("Invalid request")
        return
    parts = callback.data.split(":")
    game_id = UUID(parts[1])
    position = parts[2]

    game = await get_game(game_id)
    if not game:
        await callback.answer("Game not found")
        return

    current_color = (
        PieceColor.WHITE
        if game.current_turn == PlayerColor.WHITE
        else PieceColor.BLACK
    )
    if (
        (current_color == PieceColor.WHITE
         and game.white_player_id != user.id)
        or (current_color == PieceColor.BLACK
            and game.black_player_id != user.id)
    ):
        await callback.answer("It's not your turn!")
        return

    board = Board.from_dict(game.board_state)

    white_name = game.white_player.first_name
    black_name = (
        game.black_player.first_name
        if game.black_player
        else "Unknown"
    )
    turn_emoji = "⚪" if game.current_turn == PlayerColor.WHITE else "⚫"
    turn_name = "White" if game.current_turn == PlayerColor.WHITE else "Black"

    text = (f"🎮 <b>Checkers Game</b>\n\n"
            f"⚪ White: {white_name}\n"
            f"⚫ Black: {black_name}\n\n"
            f"Current turn: {turn_emoji} {turn_name}")

    keyboard = create_board_keyboard(
        board, str(game.id), current_color, selected_pos=position
    )
    await edit_game_message(callback, text, keyboard)
    await callback.answer(f"Selected {position}")


@router.callback_query(F.data.startswith("deselect:"))
async def handle_deselect_piece(callback: CallbackQuery, user: User) -> None:
    if not callback.data:
        await callback.answer("Invalid request")
        return
    game_id = UUID(callback.data.split(":")[1])

    game = await get_game(game_id)
    if not game:
        await callback.answer("Game not found")
        return

    board = Board.from_dict(game.board_state)
    current_color = (
        PieceColor.WHITE
        if game.current_turn == PlayerColor.WHITE
        else PieceColor.BLACK
    )

    white_name = game.white_player.first_name
    black_name = (
        game.black_player.first_name
        if game.black_player
        else "Unknown"
    )
    turn_emoji = "⚪" if game.current_turn == PlayerColor.WHITE else "⚫"
    turn_name = "White" if game.current_turn == PlayerColor.WHITE else "Black"

    text = (f"🎮 <b>Checkers Game</b>\n\n"
            f"⚪ White: {white_name}\n"
            f"⚫ Black: {black_name}\n\n"
            f"Current turn: {turn_emoji} {turn_name}")

    keyboard = create_board_keyboard(board, str(game.id), current_color)
    await edit_game_message(callback, text, keyboard)
    await callback.answer("Deselected")


@router.callback_query(F.data.startswith("move:"))
async def handle_move(callback: CallbackQuery, user: User) -> None:
    if not callback.data:
        await callback.answer("Invalid request")
        return
    parts = callback.data.split(":")
    game_id = UUID(parts[1])
    move_str = parts[2]
    from_pos, to_pos = move_str.split("-")

    game = await get_game(game_id)
    if not game:
        await callback.answer("Game not found")
        return

    current_color = (
        PieceColor.WHITE
        if game.current_turn == PlayerColor.WHITE
        else PieceColor.BLACK
    )
    if (
        (current_color == PieceColor.WHITE
         and game.white_player_id != user.id)
        or (current_color == PieceColor.BLACK
            and game.black_player_id != user.id)
    ):
        await callback.answer("It's not your turn!")
        return

    board = Board.from_dict(game.board_state)

    valid_moves = board.get_valid_moves(from_pos, current_color)
    move = next((m for m in valid_moves if m.to_pos == to_pos), None)

    if not move:
        await callback.answer("Invalid move!")
        return

    board.execute_move(move)

    continue_capturing = False
    if move.is_capture:
        piece = board.get_piece(to_pos)
        if piece:
            further_captures = board._get_single_captures(to_pos, piece)
            if further_captures:
                continue_capturing = True

    is_over, winner_color = board.is_game_over()

    if is_over:
        winner_id = None
        if winner_color == PieceColor.WHITE:
            winner_id = game.white_player_id
        elif winner_color == PieceColor.BLACK:
            winner_id = game.black_player_id

        await finish_game(game_id, winner_id)

        winner_name = (
            "White" if winner_color == PieceColor.WHITE else "Black"
        )
        black_name = (
            game.black_player.first_name
            if game.black_player
            else 'Unknown'
        )
        text = (f"🎮 <b>Checkers Game - Finished</b>\n\n"
                f"⚪ White: {game.white_player.first_name}\n"
                f"⚫ Black: {black_name}\n\n"
                f"🏆 Winner: {winner_name}!")

        await edit_game_message(callback, text)
        await callback.answer(f"Game Over! {winner_name} wins!")
        return

    game.board_state = board.to_dict()

    if not continue_capturing:
        game.current_turn = (
            PlayerColor.BLACK
            if game.current_turn == PlayerColor.WHITE
            else PlayerColor.WHITE
        )

    if continue_capturing:
        keyboard = create_board_keyboard(
            board, str(game.id), current_color, selected_pos=to_pos
        )
        if callback.message and hasattr(callback.message, 'edit_reply_markup'):
            await callback.message.edit_reply_markup(reply_markup=keyboard)
        elif callback.inline_message_id and callback.bot:
            await callback.bot.edit_message_reply_markup(
                inline_message_id=callback.inline_message_id,
                reply_markup=keyboard
            )
    else:
        white_name = game.white_player.first_name
        black_name = (
            game.black_player.first_name
            if game.black_player
            else "Unknown"
        )
        turn_emoji = (
            "⚪" if game.current_turn == PlayerColor.WHITE else "⚫"
        )
        turn_name = (
            "White" if game.current_turn == PlayerColor.WHITE else "Black"
        )
        next_color = (
            PieceColor.WHITE
            if game.current_turn == PlayerColor.WHITE
            else PieceColor.BLACK
        )
        text = (f"🎮 <b>Checkers Game</b>\n\n"
                f"⚪ White: {white_name}\n"
                f"⚫ Black: {black_name}\n\n"
                f"Current turn: {turn_emoji} {turn_name}")
        keyboard = create_board_keyboard(board, str(game.id), next_color)
        await edit_game_message(callback, text, keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("draw:"))
async def handle_draw_proposal(callback: CallbackQuery, user: User) -> None:
    if not callback.data:
        await callback.answer("Invalid request")
        return
    game_id = UUID(callback.data.split(":")[1])

    game = await get_game(game_id)
    if not game:
        await callback.answer("Game not found")
        return

    if game.status != GameStatus.ACTIVE:
        await callback.answer("Game is not active")
        return

    if user.id not in [game.white_player_id, game.black_player_id]:
        await callback.answer("You are not playing in this game!")
        return

    await callback.answer("Draw proposal sent!", show_alert=True)

    white_name = game.white_player.first_name
    black_name = (
        game.black_player.first_name
        if game.black_player
        else "Unknown"
    )
    turn_emoji = "⚪" if game.current_turn == PlayerColor.WHITE else "⚫"
    turn_name = "White" if game.current_turn == PlayerColor.WHITE else "Black"
    proposer_name = user.first_name

    text = (f"🎮 <b>Checkers Game</b>\n\n"
            f"⚪ White: {white_name}\n"
            f"⚫ Black: {black_name}\n\n"
            f"Current turn: {turn_emoji} {turn_name}\n\n"
            f"🏳️ {proposer_name} proposes a draw!")

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Accept Draw",
            callback_data=f"draw_accept:{game_id}"
        ),
        InlineKeyboardButton(
            text="❌ Decline Draw",
            callback_data=f"draw_decline:{game_id}"
        )
    )

    await edit_game_message(callback, text, builder.as_markup())


@router.callback_query(F.data.startswith("draw_accept:"))
async def handle_draw_accept(callback: CallbackQuery, user: User) -> None:
    if not callback.data:
        await callback.answer("Invalid request")
        return
    game_id = UUID(callback.data.split(":")[1])

    game = await finish_game(game_id, None)

    if game:
        black_name = (
            game.black_player.first_name
            if game.black_player
            else 'Unknown'
        )
        text = (f"🎮 <b>Checkers Game - Draw</b>\n\n"
                f"⚪ White: {game.white_player.first_name}\n"
                f"⚫ Black: {black_name}\n\n"
                f"🤝 Game ended in a draw!")

        await edit_game_message(callback, text)
        await callback.answer("Draw accepted!")
    else:
        await callback.answer("Error accepting draw")


@router.callback_query(F.data.startswith("draw_decline:"))
async def handle_draw_decline(callback: CallbackQuery, user: User) -> None:
    if not callback.data:
        await callback.answer("Invalid request")
        return
    game_id = UUID(callback.data.split(":")[1])

    game = await get_game(game_id)
    if not game:
        await callback.answer("Game not found")
        return

    board = Board.from_dict(game.board_state)
    current_color = (
        PieceColor.WHITE
        if game.current_turn == PlayerColor.WHITE
        else PieceColor.BLACK
    )

    white_name = game.white_player.first_name
    black_name = (
        game.black_player.first_name
        if game.black_player
        else "Unknown"
    )
    turn_emoji = "⚪" if game.current_turn == PlayerColor.WHITE else "⚫"
    turn_name = "White" if game.current_turn == PlayerColor.WHITE else "Black"

    text = (f"🎮 <b>Checkers Game</b>\n\n"
            f"⚪ White: {white_name}\n"
            f"⚫ Black: {black_name}\n\n"
            f"Current turn: {turn_emoji} {turn_name}")

    keyboard = create_board_keyboard(board, str(game.id), current_color)
    await edit_game_message(callback, text, keyboard)
    await callback.answer("Draw declined. Game continues!")


@router.callback_query(F.data.startswith("surrender:"))
async def handle_surrender(callback: CallbackQuery, user: User) -> None:
    if not callback.data:
        await callback.answer("Invalid request")
        return
    game_id = UUID(callback.data.split(":")[1])

    game = await get_game(game_id)
    if not game:
        await callback.answer("Game not found")
        return

    if game.status != GameStatus.ACTIVE:
        await callback.answer("Game is not active")
        return

    if user.id not in [game.white_player_id, game.black_player_id]:
        await callback.answer("You are not playing in this game!")
        return

    await callback.answer("Confirm surrender?", show_alert=True)

    white_name = game.white_player.first_name
    black_name = (
        game.black_player.first_name
        if game.black_player
        else "Unknown"
    )
    turn_emoji = "⚪" if game.current_turn == PlayerColor.WHITE else "⚫"
    turn_name = "White" if game.current_turn == PlayerColor.WHITE else "Black"

    text = (f"🎮 <b>Checkers Game</b>\n\n"
            f"⚪ White: {white_name}\n"
            f"⚫ Black: {black_name}\n\n"
            f"Current turn: {turn_emoji} {turn_name}\n\n"
            f"🏴 {user.first_name} wants to surrender!")

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Confirm Surrender",
            callback_data=f"surrender_confirm:{game_id}"
        ),
        InlineKeyboardButton(
            text="❌ Cancel",
            callback_data=f"surrender_cancel:{game_id}"
        )
    )

    await edit_game_message(callback, text, builder.as_markup())


@router.callback_query(F.data.startswith("surrender_confirm:"))
async def handle_surrender_confirm(
    callback: CallbackQuery, user: User
) -> None:
    if not callback.data:
        await callback.answer("Invalid request")
        return
    game_id = UUID(callback.data.split(":")[1])

    game = await get_game(game_id)
    if not game:
        await callback.answer("Game not found")
        return

    if user.id == game.white_player_id:
        winner_id = game.black_player_id
        winner_name = "Black"
    else:
        winner_id = game.white_player_id
        winner_name = "White"

    await finish_game(game_id, winner_id)

    black_name = (
        game.black_player.first_name
        if game.black_player
        else 'Unknown'
    )
    text = (f"🎮 <b>Checkers Game - Finished</b>\n\n"
            f"⚪ White: {game.white_player.first_name}\n"
            f"⚫ Black: {black_name}\n\n"
            f"🏆 {winner_name} wins by surrender!")

    await edit_game_message(callback, text)
    await callback.answer(f"{winner_name} wins!")


@router.callback_query(F.data.startswith("surrender_cancel:"))
async def handle_surrender_cancel(
    callback: CallbackQuery, user: User
) -> None:
    if not callback.data:
        await callback.answer("Invalid request")
        return
    game_id = UUID(callback.data.split(":")[1])

    game = await get_game(game_id)
    if not game:
        await callback.answer("Game not found")
        return

    board = Board.from_dict(game.board_state)
    current_color = (
        PieceColor.WHITE
        if game.current_turn == PlayerColor.WHITE
        else PieceColor.BLACK
    )

    white_name = game.white_player.first_name
    black_name = (
        game.black_player.first_name
        if game.black_player
        else "Unknown"
    )
    turn_emoji = "⚪" if game.current_turn == PlayerColor.WHITE else "⚫"
    turn_name = "White" if game.current_turn == PlayerColor.WHITE else "Black"

    text = (f"🎮 <b>Checkers Game</b>\n\n"
            f"⚪ White: {white_name}\n"
            f"⚫ Black: {black_name}\n\n"
            f"Current turn: {turn_emoji} {turn_name}")

    keyboard = create_board_keyboard(board, str(game.id), current_color)
    await edit_game_message(callback, text, keyboard)
    await callback.answer("Surrender cancelled. Game continues!")


@router.callback_query(F.data == "noop")
async def handle_noop(callback: CallbackQuery) -> None:
    await callback.answer()
