from aiogram import types
from aiogram.dispatcher import Dispatcher
from keyboards import UserKeyboard
from create_bot import bot, dp
from utils.database import database
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio

class FSMNard(StatesGroup):
    first_cube = State()
    second_cube = State()

class FSMMove(StatesGroup):
    move = State()



class User:
    def __init__(self, user_id):
        Global.users[user_id] = self
        self.user_id = user_id
        self.move = 0
        self.distance = 0
        self.game = 1
        self.move_info = 0

    async def update_mean(self, mean):
        self.move += 1
        self.distance += int(mean['move'])
        mean_1 = max(mean['first_cube'], mean['second_cube'])
        mean_2 = min(mean['first_cube'], mean['second_cube'])

        database.execute_nowait(sql=f"INSERT INTO meaning(game, login, meaning_1, meaning_2, move) VALUES(?, ?, ?, ?, ?)", params=(self.game, self.user_id, mean_1, mean_2, mean['move']))

    async def create(self):
        database.execute_nowait(sql=f"INSERT OR IGNORE INTO users(login) VALUES(?)", params=(self.user_id,))

    async def send_message(self, text, keyboard=None):
        await bot.send_message(chat_id=self.user_id, text=text, reply_markup=keyboard)

    async def end_game(self, status):
        database.execute_nowait(f"INSERT INTO games(game, login, moves, distance, winner) VALUES(?, ?, ?, ?, ?)", params=(self.game, self.user_id, self.move, self.distance, status))
        self.game += 1
        self.move = 0
        self.distance = 0

    async def most_frequent_pair(self, arr):
        frequency = {}
        
        for pair in arr:
            pair_tuple = tuple(pair)
            if pair_tuple in frequency:
                frequency[pair_tuple] += 1
            else:
                frequency[pair_tuple] = 1

        most_common_pair = max(frequency, key=frequency.get)
        return most_common_pair

    async def get_stats(self):
        try: 
            all_game = await database.execute(sql=f"SELECT COUNT(*) FROM games WHERE login={self.user_id}")
            win_game = await database.execute(sql=f"SELECT COUNT(*) FROM games WHERE login={self.user_id} AND winner={1}")
            pairs = await database.execute(sql=f"SELECT meaning_1, meaning_2 FROM meaning WHERE login={self.user_id}")
            distance = await database.execute(sql=f"SELECT SUM(distance) FROM games WHERE login={self.user_id}")
            moves = await database.execute(sql=f"SELECT SUM(moves) FROM games WHERE login={self.user_id}")
            distance_per_step = distance[0][0]/moves[0][0]
            move_per_game = moves[0][0]/all_game[0][0]
            
            most_pair = await self.most_frequent_pair(pairs)
            return all_game[0][0], win_game[0][0], most_pair, distance_per_step, move_per_game
        except:
            return 0, 0, (0, 0), 0, 0
    
class Global:
    users = dict()
    @classmethod
    async def get_user_by_id(cls, user_id) -> User:
        if user_id in cls.users:
            return cls.users[user_id]
        else:
            usr = User(user_id)
            await usr.create()
            return usr


@dp.callback_query_handler()
async def callback(callback: types.CallbackQuery):   
    call = callback.data.split(':')
    usr = await Global.get_user_by_id(int(call[1])) 
    if call[0] == 'change':
        await FSMNard.first_cube.set()
        await usr.send_message('Что выпало на 1 кубике', UserKeyboard.cubes_keyboard())
    elif call[0] == 'change_move':
        await FSMMove.move.set()
        await usr.send_message('Какое расстояние прошёл?', UserKeyboard.move_keyboard(usr.move_info['first_cube'], usr.move_info['second_cube']))

    await callback.answer()
        



async def start(msg: types.Message):
    usr = await Global.get_user_by_id(msg.from_user.id)
    await usr.send_message(text='Член', keyboard=UserKeyboard.start_keyboard())


async def statistics(msg: types.Message):
    usr = await Global.get_user_by_id(msg.from_user.id)
    all_game, win_game, pair, distance_per_ster, move_per_game = await usr.get_stats()
    await usr.send_message(f"Всего игр: {all_game}\n" + 
                           f'Побед: {win_game}\n' + 
                           f'Средняя дистанция за ход: {round(distance_per_ster, 2)}\n'+ 
                           f'Среднее кол-во ходов за игру: {round(move_per_game)}\n' + 
                           f"Пара кубиков: {pair}", UserKeyboard.stats_keyboard())


async def game(msg: types.Message):
    usr = await Global.get_user_by_id(msg.from_user.id)
    if msg.text == 'Следующий ход':
        await usr.update_mean(usr.move_info)
        
    await FSMNard.first_cube.set()
    await usr.send_message('Что выпало на 1 кубике', UserKeyboard.cubes_keyboard())

async def first_cube(msg: types.Message, state=FSMContext):
    usr = await Global.get_user_by_id(msg.from_user.id)
    async with state.proxy() as data:
        data['first_cube'] = int(msg.text)
    await FSMNard.next()
    await usr.send_message('Что выпало на 2 кубике', UserKeyboard.cubes_keyboard())
    
async def second_cube(msg: types.Message, state=FSMContext):
    usr = await Global.get_user_by_id(msg.from_user.id)
    async with state.proxy() as data:
        data['second_cube'] = int(msg.text)
    if data['first_cube'] == data['second_cube']:
        move = data['first_cube']*4
    else:
        move = data['first_cube'] + data['second_cube']
    usr.move_info ={
        'first_cube': data['first_cube'],
        'second_cube': data['second_cube'],
        'move': move
    }
    await state.finish()
    await usr.send_message('Продолжаем', UserKeyboard.next_step())
    await usr.send_message('Внести изменения', UserKeyboard.error(usr.user_id))

    

async def end_game(msg: types.Message):
    usr = await Global.get_user_by_id(msg.from_user.id)
    await usr.update_mean(usr.move_info)
    await usr.send_message('Кто победил?', UserKeyboard.who_win())


async def lose(msg: types.Message):
    usr = await Global.get_user_by_id(msg.from_user.id)
    await usr.end_game(status=False)
    await usr.send_message('Повезет в следующий раз', UserKeyboard.start_keyboard())

async def win(msg: types.Message):
    usr = await Global.get_user_by_id(msg.from_user.id)
    await usr.end_game(status=True)
    await usr.send_message('Поздравляю с победой', UserKeyboard.start_keyboard())

async def stat_per_game(msg: types.Message):
    usr = await Global.get_user_by_id(msg.from_user.id)
    await usr.send_message('Пока нету', UserKeyboard.back())

async def change_move(msg: types.Message, state: FSMContext):
    usr = await Global.get_user_by_id(msg.from_user.id)
    async with state.proxy() as data:
        data['move'] = msg.text
    usr.move_info['move'] = data['move']
    await state.finish()
    await usr.send_message('Продолжаем', UserKeyboard.next_step())


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start, text=['Назад', '/start'])
    dp.register_message_handler(statistics, text='Статистика')
    dp.register_message_handler(end_game, text='Игра закончена')
    dp.register_message_handler(game, text=['Играть', 'Следующий ход'], state=None)
    dp.register_message_handler(first_cube, state=FSMNard.first_cube)
    dp.register_message_handler(second_cube, state=FSMNard.second_cube)
    dp.register_message_handler(lose, text='Оппонент')
    dp.register_message_handler(win, text='Я')
    dp.register_message_handler(stat_per_game, text='Статистика по играм')
    dp.register_message_handler(change_move, state=FSMMove.move)





    
