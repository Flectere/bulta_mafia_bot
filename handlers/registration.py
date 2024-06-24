from aiogram import Router, Bot, F
from aiogram.types import Message
from aiogram.filters import Command, BaseFilter

from typing import List

import keyboards as kb

import texts

from callbacks import game_settings
from callbacks.game_process import Mafia, Don, Doctor, Player, Maniac, Inspector, Sheriff

import random


active_users = []

live_players : List[Player] = [] 

game_chat_id = 0

play_writed = False

registration_start = False

game_start = False


class RegistrationFilter(BaseFilter):  
    async def __call__(self, message: Message) -> bool:
        return not game_start

game_registration_router = Router()
game_registration_router.message.filter(RegistrationFilter())

async def role_distribution(bot: Bot):
    """распределение ролей между игроками"""
    for i in active_users:
        role = random.choice(game_settings.active_roles)
        if role == game_settings.roles[0]:
            live_players.append(Mafia(i))
        elif role == game_settings.roles[1]:
            live_players.append(Don(i))
        elif role == game_settings.roles[2]:
            live_players.append(Doctor(i))
        elif role == game_settings.roles[3]:
            live_players.append(Sheriff(i))
        elif role == game_settings.roles[4]:
            live_players.append(Player(i))
        elif role == game_settings.roles[6]:
            live_players.append(Maniac(i))
        elif role == game_settings.roles[7]:
            live_players.append(Inspector(i))
        await bot.send_message(chat_id = i.id, text = texts.descriptions_dict[role])
        game_settings.active_roles.remove(role)
    active_users.clear()
    mafias = [player for player in live_players if isinstance(player, Mafia)]
    don = [player for player in live_players if isinstance(player, Don)][0]
    for mafia in mafias:
        await bot.send_message(chat_id = mafia.id, text = f"Твой дон это <b>{don}</b>, а вся семья - <b>{', '.join([mafia.__str__() for mafia in mafias])}</b>")
    if len(mafias) != 0:
        await bot.send_message(chat_id = don.id, text = f"Твои помощники это <b>{', '.join([mafia.__str__() for mafia in mafias])}</b> они будут тебе советовать кого убить ночью. Но помни что конечное решение за <b>тобой</b>!")


@game_registration_router.message(Command('game'), F.chat.type == 'supergroup')
async def game_registration_cmd(message:Message):
    global registration_start, game_chat_id
    if not registration_start:
        game_chat_id = message.chat.id
        message.chat.type
        registration_start = True
        await message.answer("Набор в игру начался, успей присоединиться (/join)!")
    else:
        await message.answer("Набор уже запущен")


@game_registration_router.message(Command('join'))
async def game_join_cmd(message:Message):
    if message.from_user not in active_users and registration_start:
        active_users.append(message.from_user)
        await message.answer(f"<b>{message.from_user.first_name}</b>, ты зачислен!")
        await message.delete()
    elif not registration_start:
        await message.answer(f"Набор в игру не начался!")
        await message.answer(f"Для того, чтобы начать игру напишите команду (/game) или нажмите в меню команд")
    else:
        await message.delete()   
        await message.answer(f"<b>{message.from_user.full_name},ты уже в списке!</b>")

@game_registration_router.message(Command('play'))
async def game_start_cmd(message:Message):
    global play_writed
    if not play_writed:    
        if len(active_users) < 4:
            await message.answer("Недостаточно игроков для начала игры.\nДля того, чтобы присоединиться, нажмите (/join)!")
        elif registration_start:
            await message.answer("Точно начать?", reply_markup = kb.select_settings_keyboard)
            play_writed = True
        else:
            await message.answer(f"Набор в игру не начался!")
            await message.answer(f"Для того, чтобы начать игру напишите команду (/game) или нажмите в меню команд")
    await message.delete()