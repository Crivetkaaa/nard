from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class UserKeyboard:
    def start_keyboard():
        btn_1 = KeyboardButton(text='Статистика')
        btn_2 = KeyboardButton(text='Играть')
        keyboard = ReplyKeyboardMarkup()
        return keyboard.add(btn_1).add(btn_2)
    
    def stats_keyboard():
        keyboard = ReplyKeyboardMarkup()
        btn_1 = KeyboardButton(text='Статистика по играм')
        btn_2 = KeyboardButton(text='Назад')
        keyboard.add(btn_1).add(btn_2)
        return keyboard
    
    def cubes_keyboard():
        keyboard = ReplyKeyboardMarkup().add(*[str(x) for x in range(1, 7)])
        return keyboard
    
    def move_keyboard(first_cube, second_cube):
        keyboard = ReplyKeyboardMarkup()
        if first_cube != second_cube:
            btn_0 = KeyboardButton("0")
            btn_1 = KeyboardButton(f"{first_cube}")
            btn_2 = KeyboardButton(f"{second_cube}")
            btn_all = KeyboardButton(f"{int(second_cube)+int(first_cube)}")

            keyboard.add(btn_all).add(btn_1, btn_2).add(btn_0)
        else:
            keyboard.add(*[str(int(second_cube)*x) for x in range(4, -1, -1)])

        return keyboard
    
    def next_step():
        keyboard = ReplyKeyboardMarkup()
        keyboard.add('Следующий ход').add('Игра закончена')
        return keyboard
    
    def who_win():
        keyboard = ReplyKeyboardMarkup()
        keyboard.add('Я').add('Оппонент')
        return keyboard
    
    def back():
        keyboard = ReplyKeyboardMarkup()
        keyboard.add('Назад')
        return keyboard
    
    def error(user_id):
        btn_1 = InlineKeyboardButton(text='Изменить бросок', callback_data=f'change:{user_id}')
        btn_2 = InlineKeyboardButton(text='Изменить расстояние', callback_data=f'change_move:{user_id}')
        keyboard = InlineKeyboardMarkup()
        keyboard.add(btn_1).add(btn_2)
        return keyboard
        
    