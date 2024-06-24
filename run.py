import asyncio

from CONFIG import TOKEN


import texts

from aiogram import Dispatcher, Bot
from aiogram.client.bot import DefaultBotProperties

from aiogram.types import Message
from aiogram.filters import Command, BaseFilter

from aiogram.types.chat_permissions import ChatPermissions

from handlers import registration

from callbacks.game_process import apscheduler

import keyboards as kb

from callbacks import game_settings, game_process

dp = Dispatcher()

@dp.message(Command("exit"))
async def on_exit(message: Message):
    await message.answer("я выключился")
    await dp.stop_polling()

@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(text = texts.help_text)   

@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Бот запущен",reply_markup = kb.add_bot_to_group_keyboard)
   
async def on_shutdown(bot: Bot):
    await bot.set_chat_permissions(chat_id = registration.game_chat_id, permissions = ChatPermissions(can_send_messages = True), use_independent_chat_permissions = False)

async def on_sturtup(bot: Bot):
    await bot.send_message(-1002129145668, "я включился")

async def start():
    apscheduler.start()
    dp.include_routers(registration.game_registration_router, game_settings.game_settings_router, game_process.night_router, game_process.day_router)
    bot = Bot(token = TOKEN, default = DefaultBotProperties(parse_mode = 'HTML'))
    dp.shutdown.register(on_shutdown)
    dp.startup.register(on_sturtup)
    await bot.delete_webhook(drop_pending_updates = True)
    await dp.start_polling(bot)
    
if __name__ == '__main__':
    asyncio.run(start())