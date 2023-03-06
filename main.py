from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile, ReplyKeyboardRemove
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext

from config import TOKEN_aiogram
from films_search import Films

storage = MemoryStorage()
bot = Bot(token=TOKEN_aiogram)
dp = Dispatcher(bot, storage=storage)

Films = Films()

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


class Choose_inf_of_title(StatesGroup):
    film_name = State()
    type_industry = State()


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    user_id = message.from_user.id
    print(user_id)
    await message.reply(f"Привет!\n Я запомнил твой ID для дальнейшей работы!\n {message.from_user.id}",
                        reply_markup=buttons)


@dp.message_handler()
async def reaction_buttons(message: types.Message):
    if message.text == 'Привет':
        await message.reply(f'пока(')
    if message.text == '🧠Информация о тайтле🧠':
        await message.reply('Напиши мне отрасль киноиндустрии', reply_markup=buttons_type)
        await Choose_inf_of_title.type_industry.set()

        # full_name, description, year, poster, rating = Films.get_film_information(message)
        # await message.reply('функция в разработке')
    if message.text == '🍿тайтлы по параметрам🍿':
        await message.reply('функция в разработке')
    if message.text == '🎁тайтл по твоим интересам🎁':
        await message.reply('функция в разработке')


@dp.message_handler(state=Choose_inf_of_title.type_industry)
async def get_type_industry(message: types.Message, state: FSMContext):
    if message.text == 'аниме':
        type_industry = 'anime'
    elif message.text == 'фильмы':
        type_industry = 'movie'
    elif message.text == 'сериалы':
        type_industry = 'tv-series'
    else:
        await message.reply('неверный тип')

    await state.update_data(type_industry=type_industry)
    await message.reply(
        'Напиши мне название фильма 🌞. Для большего процента успеха, советую написать максимально правильно🤔',
        reply_markup=ReplyKeyboardRemove())
    await Choose_inf_of_title.film_name.set()


@dp.message_handler(state=Choose_inf_of_title.film_name)
async def get_film_inf(message: types.Message, state: FSMContext):
    await state.update_data(film=message.text)
    await message.answer('Отлично👍, осуществляю поиск')
    data = await state.get_data()
    film = data['film']
    type_industry = data['type_industry']
    await state.finish()
    print('get name')
    full_name, description, year, poster, rating = Films.get_film_information(film, type_industry)
    if full_name == False:
        await message.reply('не удалось найти фильм', reply_markup=buttons)
    else:
        await bot.send_photo(chat_id=message.chat.id, photo=InputFile('img.png'),
                             caption=f'🌟{full_name}🌟\n💥{description}💥\nгод - 🌜{year}🌛\n 📈рейтинг кинопоиска - {rating} 📈',
                             reply_markup=buttons, )
    print(message.from_user.id)


if __name__ == '__main__':
    executor.start_polling(dp)
