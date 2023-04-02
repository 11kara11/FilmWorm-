from aiogram import Dispatcher, types
from aiogram.types import Message
from create_bot import dp, bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.filters import Text
from films_search import Films
from users import User
from usertofilm import UserToFilm
import db_session
import requests

Films = Films()
user = User()
user_to_film = UserToFilm()


@dp.message_handler(lambda message: '🎁тайтл по твоим интересам🎁' in message.text.lower())
async def reaction_buttons_f3(message: types.Message, state: FSMContext):
    if message.text == '🎁тайтл по твоим интересам🎁':
        db_sess = db_session.create_session()
        if db_sess.query(UserToFilm).filter(UserToFilm.id == message.from_user.id).count() >= 3:
            await message.reply('ща порекомендую')
            liked_films = (db_sess.query(UserToFilm).filter_by(id=message.from_user.id).all())
            for i in liked_films:
                print(i.film_id)


def register_handler_f3(dp: Dispatcher):
    dp.register_message_handler(reaction_buttons_f3)