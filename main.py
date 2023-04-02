from aiogram.utils import executor
import db_session
from create_bot import dp, bot
from inf_of_title import register_handler_f1, buttons
from title_on_param import register_handler_f2
from films_on_interest import register_handler_f3

print('бот запущен')

register_handler_f1(dp)
register_handler_f2(dp)
register_handler_f3(dp)

if __name__ == '__main__':
    db_session.global_init("db/users.db")
    executor.start_polling(dp)
