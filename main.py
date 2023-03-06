from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

from config import TOKEN


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


button_information_film = KeyboardButton('Информация о фильме')
button_rec_on_param = KeyboardButton('фильмы по параметрам')
button_rec_for_user = KeyboardButton('Фильм по твоим интересам')
buttons = ReplyKeyboardMarkup(resize_keyboard=True).row(button_information_film, button_rec_on_param)
buttons.add(button_rec_for_user)

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    user_id = message.from_user.id
    print(user_id)
    await message.reply(f"Привет!\n Я запомнил твой ID для дальнейшей работы!\n {message.from_user.id}", reply_markup=buttons)



@dp.message_handler()
async def reaction_buttons(message: types.Message):
    if message.text == 'Привет':
        await message.reply(f'пока(')
    if message.text == 'Информация о фильме':
        await message.reply('функция в разработке')
    if message.text == 'фильмы по параметрам':
        await message.reply('функция в разработке')
    if message.text == 'Фильм по твоим интересам':
        await message.reply('функция в разработке')




if __name__ == '__main__':
    executor.start_polling(dp)
