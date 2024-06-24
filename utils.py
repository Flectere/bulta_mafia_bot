from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# def night_kb(content):
#     builder = InlineKeyboardBuilder()
#     if isinstance(content, str):
#         content = [content]
#     [builder.button(text = txt.user.full_name, callback_data=f'{txt.user.full_name}') for txt in content]
#     builder.adjust(1)
#     return builder.as_markup()

