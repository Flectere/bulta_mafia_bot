from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from callbacks import game_process


go_to_bot_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = "Перейти в бот", url = "https://t.me/bulta_mafia_bot")]])

add_bot_to_group_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = "Добавить бота в чат", url = "t.me/bulta_mafia_bot?startgroup")]])

manual_settings_buttons = [
            [InlineKeyboardButton(text='Добавить мафию',callback_data='edit_mafia')],
            [InlineKeyboardButton(text='Добавить доктора',callback_data='edit_doctor')],
            [InlineKeyboardButton(text='Добавить комиссара',callback_data='edit_sheriff')],
            [InlineKeyboardButton(text='Сохранить', callback_data='save_settings')]
            ]
manual_role_settings_keyboard = InlineKeyboardMarkup(inline_keyboard=manual_settings_buttons)


select_settings_buttons=[[InlineKeyboardButton(text='Начать игру', callback_data='start_game')]]
select_settings_keyboard = InlineKeyboardMarkup(inline_keyboard = select_settings_buttons)

edit_mafia_buttons = [
    [InlineKeyboardButton(text='➕',callback_data='plus_mafia'),InlineKeyboardButton(text='➖',callback_data='minus_mafia')],
    [InlineKeyboardButton(text='Назад',callback_data='go_back')]]
edit_mafia_keyboard = InlineKeyboardMarkup(inline_keyboard=edit_mafia_buttons)

edit_doctor_buttons = [
    [InlineKeyboardButton(text='➕',callback_data='plus_doctor'),InlineKeyboardButton(text='➖',callback_data='minus_doctor')],
    [InlineKeyboardButton(text='Назад',callback_data='go_back')]]
edit_doctor_keyboard = InlineKeyboardMarkup(inline_keyboard=edit_doctor_buttons)

edit_sheriff_buttons = [
    [InlineKeyboardButton(text='➕',callback_data='plus_sheriff'),InlineKeyboardButton(text='➖',callback_data='minus_sheriff')],
    [InlineKeyboardButton(text='Назад',callback_data='go_back')]]
edit_sheriff_keyboard = InlineKeyboardMarkup(inline_keyboard=edit_sheriff_buttons)
