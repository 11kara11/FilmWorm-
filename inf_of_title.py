from aiogram import Dispatcher, types
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


class Choose(StatesGroup):
    film_name = State()
    type_industry = State()


'''
these handlers get the type of industry and the name of the movie, and then contact the api to get the data
'''


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    user_id = message.from_user.id
    print(user_id)
    await message.reply(f"Привет, {message.from_user.full_name}!\n Я запомнил твой ID для дальнейшей работы!\n",
                        reply_markup=buttons)
    db_sess = db_session.create_session()
    if db_sess.query(User).filter_by(id=message.from_user.id).count() < 1:
        user = User()
        user.id = message.from_user.id
        db_sess.add(user)
        db_sess.commit()
        db_sess.close()


@dp.message_handler(lambda message: '🧠Информация о тайтле🧠' in message.text)
async def reaction_buttons_f1(message: types.Message):
    # if message.text == 'Привет':
    # await message.reply(f'пока(')
    if message.text == '🧠Информация о тайтле🧠':
        await message.reply('Напиши мне отрасль киноиндустрии', reply_markup=buttons_type)
        await Choose.type_industry.set()

        # full_name, description, year, poster, rating = Films.get_film_information(message)
        # await message.reply('функция в разработке')
    # if message.text == '🎁тайтл по твоим интересам🎁':
    # await message.reply('функция в разработке')


@dp.message_handler(state=Choose.type_industry)
async def get_type_industry(message: types.Message, state: FSMContext):
    if message.text == 'аниме':
        type_industry = 'anime'
    elif message.text == 'фильмы':
        type_industry = 'movie'
    elif message.text == 'сериалы':
        type_industry = 'tv-series'
    else:
        await message.reply('неверный тип, выбери из предложенных', reply_markup=buttons_type)
        type_industry = False
    if type_industry:
        await state.update_data(type_industry=type_industry)
        await message.reply(
            'Напиши мне название фильма 🌞. Для большего процента успеха, советую написать максимально правильно🤔',
            reply_markup=ReplyKeyboardRemove())
        await Choose.film_name.set()


@dp.message_handler(state=Choose.film_name)
async def get_film_inf(message: types.Message, state: FSMContext):
    await state.update_data(film=message.text)
    await message.answer('Отлично👍, осуществляю поиск')
    data = await state.get_data()
    film = data['film']
    type_industry = data['type_industry']
    await state.finish()
    print('get name')
    full_name, description, year, poster, rating, id_film = Films().get_film_information(film, type_industry)
    if full_name == False:
        await message.reply('не удалось найти фильм', reply_markup=buttons)
    else:
        button_like = InlineKeyboardButton('like', callback_data=f'buttonlikedinf_{id_film}')
        buttons_inline = InlineKeyboardMarkup().add(button_like)
        await bot.send_photo(chat_id=message.chat.id, photo=InputFile('img.png'),
                             caption=f'🌟{full_name}🌟\n💥{description}💥\nгод - 🌜{year}🌛\n 📈рейтинг кинопоиска - {rating} 📈',
                             reply_markup=buttons_inline, )
        await bot.send_message(chat_id=message.chat.id, text='если тебе понравился тайтл, ты можешь лайкнуть его :)',
                               reply_markup=buttons)
    print(message.from_user.id)


'''
inline like button, creates a new session to the database and checks
if there is a record where id user in telegram == id user in db and id liked film == id film in db ? 
if yes, then it skips, if not, it creates a new record
'''


@dp.callback_query_handler(lambda callback_query: "buttonlikedinf" in callback_query.data)
async def process_callback_buttonlike(callback_query: types.CallbackQuery):
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
    db_sess.close()
    await callback_query.answer()


def register_handler_f1(dp: Dispatcher):
    dp.register_message_handler(process_start_command, commands=['start'])
    dp.register_message_handler(reaction_buttons_f1)
    dp.register_message_handler(get_type_industry)
    dp.register_message_handler(get_film_inf)
    dp.register_poll_handler(process_callback_buttonlike)
