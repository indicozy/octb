from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, ReplyKeyboardRemove

BASE_BUTTONS = ReplyKeyboardMarkup([
    [
        'Купить/Продать',
        'Мои Объявления',
    ]
], one_time_keyboard=True)