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
button_information_film = KeyboardButton('🧠Информация о тайтле🧠')
button_rec_on_param = KeyboardButton('🍿тайтлы по параметрам🍿')
button_rec_for_user = KeyboardButton('🎁тайтл по твоим интересам🎁')
buttons = ReplyKeyboardMarkup(resize_keyboard=True).row(button_information_film, button_rec_on_param)
buttons.add(button_rec_for_user)


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
button_continue = KeyboardButton('Продолжить')
reply_genre_buttons = ReplyKeyboardMarkup().add(button_continue)
reply_genre_buttons.add(*buttons_genre)
genres = [
    'боевик', 'аниме', 'биография', 'детектив', 'документальный', 'комедия', 'драма', 'криминал', 'мелодрама',
    'мультфильм', 'мюзикл', 'приключения', 'спорт', 'триллер', 'ужасы', 'фантастика', 'фэнтези',
]

button_skip = KeyboardButton('Пропустить')
reply_button_skip = ReplyKeyboardMarkup(resize_keyboard=True).add(button_skip)


class Choose(StatesGroup):
    choose_genre = State()
    choose_year = State()
    choose_country = State()


@dp.message_handler(lambda message: '🍿тайтлы по параметрам🍿' in message.text.lower())
async def reaction_buttons_f2(message: types.Message, state: FSMContext):
    if message.text == '🍿тайтлы по параметрам🍿':
        await message.reply('Выбери до 4 жанров, ты можешь написать "Продолжить" для завершения выбора',
                            reply_markup=reply_genre_buttons)
        await state.finish()
        await Choose.choose_genre.set()
        await state.update_data(params={"genres.name": []})
    else:
        print(message.text)


@dp.message_handler(lambda message: message.text in genres or message.text.lower() == 'продолжить',
                    state=Choose.choose_genre)
async def get_genres(message: types.Message, state: FSMContext):
    params = await state.get_data('params')
    print(params)
    if message.text.lower() == 'продолжить':
        if 1 <= len(params['params']['genres.name']) <= 4:
            await Choose.choose_year.set()
            await message.reply('напиши мне год выпуска фильма, ты можешь пропустить этот параметр',
                                reply_markup=reply_button_skip)
            print(params)
        else:
            await message.reply('выбери хотя бы 1 жанр')
    else:
        print(message.text)
    if message.text in genres:
        if len(params['params']['genres.name']) < 4:
            if message.text not in params['params']['genres.name']:
                params['params']['genres.name'].append(message.text)
                await state.update_data(params=params['params'])
                await message.reply(f'выбранные жанры:\n{params["params"]["genres.name"]}')
                print(params)
            else:
                await message.reply('ты уже выбрал этот жанр, давай другой')
        if len(params['params']['genres.name']) == 4:
            await message.reply('напиши мне год выпуска фильма, ты можешь пропустить этот параметр',
                                reply_markup=reply_button_skip)
            await Choose.choose_year.set()
            print(params)


@dp.message_handler(state=Choose.choose_year)
async def get_year(message: types.Message, state: FSMContext):
    if message.text == 'Пропустить':
        await message.reply(
            'напиши мне страну производства, старайся написать максимально праивльно, ты можешь пропустить этот пункт',
            reply_markup=reply_button_skip)
        await state.update_data(year=None)
        await Choose.choose_country.set()
    elif str(message.text).isdigit():
        await message.reply(
            'напиши мне страну производства, старайся написать максимально праивльно, ты можешь пропустить этот пункт',
            reply_markup=reply_button_skip)
        await state.update_data(year=int(message.text))
        await Choose.choose_country.set()
    else:
        await message.reply('хм, кажется это не год')
        await Choose.choose_year.set()


@dp.message_handler(state=Choose.choose_country)
async def get_country(message: types.Message, state: FSMContext):
    if message.text == 'Пропустить':
        await state.update_data(country=None)
    else:
        await state.update_data(country=message.text)
    await message.reply('Начинаю поиск', reply_markup=buttons)
    data = await state.get_data()
    params = data['params']
    year = data['year']
    country = data['country']
    await state.finish()
    try:
        title_json = await Films.get_title_on_param(params, year, country)
        full_name = title_json['docs'][0]['name']
        description = title_json['docs'][0]['description']
        year = title_json['docs'][0]['year']
        id_film = title_json['docs'][0]['id']
        poster_link = title_json['docs'][0]['poster']['url']
        rating = title_json['docs'][0]['rating']['kp']
        poster = requests.get(poster_link)
        with open('img.png', 'wb') as photo:
            photo.write(poster.content)

        await state.update_data(i=0)
        await state.update_data(title_json=title_json)
        button_like = InlineKeyboardButton('like', callback_data=f'buttonlikedparam_{id_film}')
        button_next = InlineKeyboardButton('next', callback_data='next')
        button_back = InlineKeyboardButton('back', callback_data='back')
        buttons_inline = InlineKeyboardMarkup().add(button_like, button_next, button_back)
        await bot.send_photo(chat_id=message.chat.id, photo=InputFile('img.png'),
                             caption=f'🌟{full_name}🌟\n💥{description}💥\nгод - 🌜{year}🌛\n 📈рейтинг кинопоиска - {rating} 📈',
                             reply_markup=buttons_inline, )
    except Exception:
        await state.finish()
        await message.reply('не удалось найти тайтл', reply_markup=buttons)
    # print(title_json)


@dp.callback_query_handler(lambda callback_query: "buttonlikedparam" in callback_query.data)
async def process_callback_buttonlike_param(callback_query: types.CallbackQuery):
    print('like')
    await bot.send_message(chat_id=callback_query.from_user.id, text='Я добавил этот тайтл в понравившиеся :)')
    data = callback_query.data.split('_')[1]
    db_sess = db_session.create_session()
    if db_sess.query(UserToFilm).filter(
            UserToFilm.id == callback_query.from_user.id, UserToFilm.film_id == data).count() < 1:
        print('add new title in db')
        user_to_film.id = callback_query.from_user.id
        user_to_film.film_id = data
        db_sess.add(user_to_film)
        db_sess.commit()
        db_sess.close()
    await callback_query.answer()
    db_sess.close()


@dp.callback_query_handler(lambda callback_query: "next" == callback_query.data)
async def process_callback_next(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    title_json = data['title_json']
    i = data['i']
    try:
        if i <= 50:
            full_name = title_json['docs'][i + 1]['name']
            description = title_json['docs'][i + 1]['description']
            year = title_json['docs'][i + 1]['year']
            id_film = title_json['docs'][i + 1]['id']
            poster_link = title_json['docs'][i + 1]['poster']['url']
            rating = title_json['docs'][i + 1]['rating']['kp']
            poster = requests.get(poster_link)
            with open('img.png', 'wb') as photo:
                photo.write(poster.content)
            button_like = InlineKeyboardButton('like', callback_data=f'buttonliked_{id_film}')
            button_next = InlineKeyboardButton('next', callback_data='next')
            button_back = InlineKeyboardButton('back', callback_data='back')
            buttons_inline = InlineKeyboardMarkup().add(button_like, button_next, button_back)
            await bot.send_photo(chat_id=callback_query.from_user.id, photo=InputFile('img.png'),
                                 caption=f'🌟{full_name}🌟\n💥{description}💥\nгод - 🌜{year}🌛\n 📈рейтинг кинопоиска - {rating} 📈',
                                 reply_markup=buttons_inline, )
            await state.update_data(i=i + 1)
        else:
            await bot.send_message(chat_id=callback_query.from_user.id,
                                   text='я не могу дальше показывать, сделай новый запрос', reply_markup=buttons)
    except Exception:
        await bot.send_message(chat_id=callback_query.from_user.id, text='тайтлы кончились', reply_markup=buttons)


@dp.callback_query_handler(lambda callback_query: "back" in callback_query.data)
async def process_callback_back(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    title_json = data['title_json']
    i = data['i']
    try:
        if i <= 50:
            full_name = title_json['docs'][i - 1]['name']
            description = title_json['docs'][i - 1]['description']
            year = title_json['docs'][i - 1]['year']
            id_film = title_json['docs'][i - 1]['id']
            poster_link = title_json['docs'][i - 1]['poster']['url']
            rating = title_json['docs'][i - 1]['rating']['kp']
            poster = requests.get(poster_link)
            with open('img.png', 'wb') as photo:
                photo.write(poster.content)
            button_like = InlineKeyboardButton('like', callback_data=f'buttonliked_{id_film}')
            button_next = InlineKeyboardButton('next', callback_data='next')
            button_back = InlineKeyboardButton('back', callback_data='back')
            buttons_inline = InlineKeyboardMarkup().add(button_like, button_next, button_back)
            await bot.send_photo(chat_id=callback_query.from_user.id, photo=InputFile('img.png'),
                                 caption=f'🌟{full_name}🌟\n💥{description}💥\nгод - 🌜{year}🌛\n 📈рейтинг кинопоиска - {rating} 📈',
                                 reply_markup=buttons_inline, )
            await state.update_data(i=i - 1)
        else:
            await bot.send_message(chat_id=callback_query.from_user.id,
                                   text='я не могу дальше показывать, сделай новый запрос', reply_markup=buttons)
    except Exception:
        await bot.send_message(chat_id=callback_query.from_user.id, text='тайтлы кончились', reply_markup=buttons)
        await state.finish()


def register_handler_f2(dp: Dispatcher):
    dp.register_message_handler(reaction_buttons_f2)
    dp.register_message_handler(get_genres)
    dp.register_message_handler(get_year)
    dp.register_message_handler(get_country)
    dp.register_poll_handler(process_callback_buttonlike_param)
    dp.register_poll_handler(process_callback_next)
    dp.register_poll_handler(process_callback_back)
    print(1)
