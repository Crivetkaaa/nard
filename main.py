from aiogram.utils import executor
import logging
from create_bot import dp
from handlers import users
from handlers.users import User



logging.basicConfig(level=logging.INFO)
users.register_handlers(dp)


async def on_startup(_):
    pass


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
