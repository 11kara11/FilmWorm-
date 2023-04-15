from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from config import TOKEN_aiogram

'''
creating the main variables for the bot to work
'''
storage = MemoryStorage()
bot = Bot(token=TOKEN_aiogram)
dp = Dispatcher(bot, storage=storage)
