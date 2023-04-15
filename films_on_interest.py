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
from collections import Counter

# user = User()
# user_to_film = UserToFilm()

button_information_film = KeyboardButton('🧠Информация о тайтле🧠')
button_rec_on_param = KeyboardButton('🍿тайтлы по параметрам🍿')
button_rec_for_user = KeyboardButton('🎁тайтл по твоим интересам🎁')
buttons = ReplyKeyboardMarkup(resize_keyboard=True).row(button_information_film, button_rec_on_param)
buttons.add(button_rec_for_user)

'''
checks if the user has 3 like movies, if yes, then establishes a connection with the database, takes the movie IDs, 
makes requests to the api and gets the genres. 
The 2 most common genres are selected and a request is made to the api with these genres
'''


@dp.message_handler(lambda message: '🎁тайтл по твоим интересам🎁' in message.text.lower())
async def reaction_buttons_f3(message: types.Message, state: FSMContext):
    genres = []
    top_genres = []
    if message.text == '🎁тайтл по твоим интересам🎁':
        db_sess = db_session.create_session()
        if db_sess.query(UserToFilm).filter(UserToFilm.id == message.from_user.id).count() >= 3:
            await message.reply('ща порекомендую')
            liked_films = (db_sess.query(UserToFilm).filter_by(id=message.from_user.id).all())
            for i in liked_films:
                title_json = await Films().get_film_on_id(i.film_id)
                # print(title_json)
                genres_list = title_json['docs'][0]['genres']
                for genre in genres_list:
                    genres.append(genre['name'])
            genre_count = Counter(genres)
            tuple_top_genres = genre_count.most_common(2)
            for genre, count in tuple_top_genres:
                top_genres.append(genre)
            try:
                title_json = await Films().get_title_on_param(params={'genres.name': top_genres})
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
                button_like = InlineKeyboardButton('like', callback_data=f'buttonlikedinterest_{id_film}')
                button_next = InlineKeyboardButton('next', callback_data='next')
                button_back = InlineKeyboardButton('back', callback_data='back')
                buttons_inline = InlineKeyboardMarkup().add(button_like, button_next, button_back)
                await bot.send_photo(chat_id=message.chat.id, photo=InputFile('img.png'),
                                     caption=f'🌟{full_name}🌟\n💥{description}💥\nгод - 🌜{year}🌛\n 📈рейтинг кинопоиска - {rating} 📈',
                                     reply_markup=buttons_inline, )
            except Exception:
                await state.finish()
                await message.reply('не удалось найти тайтл', reply_markup=buttons)
        else:
            await message.reply('полайкай еще фильмов, ято бы я мог советовать на твой вкус')


'''
inline like button, creates a new session to the database and checks
if there is a record where id user in telegram == id user in db and id liked film == id film in db ? 
if yes, then it skips, if not, it creates a new record
'''


@dp.callback_query_handler(lambda callback_query: "buttonlikedinterest" in callback_query.data)
async def process_callback_buttonlike_interest(callback_query: types.CallbackQuery):
    print('like')
    await bot.send_message(chat_id=callback_query.from_user.id, text='Я добавил этот тайтл в понравившиеся :)')
    data = callback_query.data.split('_')[1]
    db_sess = db_session.create_session()
    if db_sess.query(UserToFilm).filter(
            UserToFilm.id == callback_query.from_user.id, UserToFilm.film_id == data).count() < 1:
        print('add new title in db')
        user_to_film = UserToFilm()
        user_to_film.id = callback_query.from_user.id
        user_to_film.film_id = data
        db_sess.add(user_to_film)
        db_sess.commit()
        # db_sess.refresh(user_to_film)
    # db_sess.expunge_all()
    db_sess.close()
    await callback_query.answer()
    print('enddddddddddddddddd')


'''
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
            button_like = InlineKeyboardButton('like', callback_data=f'buttonlikedinterest_{id_film}')
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
            button_like = InlineKeyboardButton('like', callback_data=f'buttonlikedinterest_{id_film}')
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

'''


def register_handler_f3(dp: Dispatcher):
    dp.register_message_handler(reaction_buttons_f3)
    dp.register_poll_handler(process_callback_buttonlike_interest)
