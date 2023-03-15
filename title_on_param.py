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


Films = Films()
user = User()
user_to_film = UserToFilm()
button_information_film = KeyboardButton('🧠Информация о тайтле🧠')
button_rec_on_param = KeyboardButton('🍿тайтлы по параметрам🍿')
button_rec_for_user = KeyboardButton('🎁тайтл по твоим интересам🎁')
buttons = ReplyKeyboardMarkup(resize_keyboard=True).row(button_information_film, button_rec_on_param)
buttons.add(button_rec_for_user)

button_anime = KeyboardButton('аниме')
button_film = KeyboardButton('фильмы')
button_serial = KeyboardButton('сериалы')
buttons_type = ReplyKeyboardMarkup(resize_keyboard=True).row(button_anime, button_film)
buttons_type.add(button_serial)

buttons_genre = [
    KeyboardButton('боевик'),
    KeyboardButton('аниме'),
    KeyboardButton('биография'),
    KeyboardButton('детектив'),
    KeyboardButton('документальный'),
    KeyboardButton('комедия'),
    KeyboardButton('драма'),
    KeyboardButton('криминал'),
    KeyboardButton('мелодрама'),
    KeyboardButton('мультфильм'),
    KeyboardButton('мюзикл'),
    KeyboardButton('приключения'),
    KeyboardButton('спорт'),
    KeyboardButton('триллер'),
    KeyboardButton('ужасы'),
    KeyboardButton('фантастика'),
    KeyboardButton('фэнтези'),

]
reply_genre_buttons = ReplyKeyboardMarkup().add(*buttons_genre)


class Choose(StatesGroup):
    pass


@dp.message_handler(lambda message: 'привет' in message.text.lower())
async def reaction_buttons_f2(message: types.Message):
    if message.text == 'Привет':
        await message.reply('функция в разработке')
    else:
        print(message.text)


def register_handler_f2(dp: Dispatcher):
    dp.register_message_handler(reaction_buttons_f2)
    print(1)
