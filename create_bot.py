from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()


token = "6058077055:AAHgLqvigiMkbSFmy-lDivjrb-GIIMpWg04"

bot = Bot(token=token)
dp = Dispatcher(bot, storage=storage) 
