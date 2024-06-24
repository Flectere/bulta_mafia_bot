from aiogram import Router, F, Bot

import random

from aiogram.types import CallbackQuery, Message, Chat
from aiogram.types.chat_permissions import ChatPermissions

from aiogram.methods.restrict_chat_member import RestrictChatMember


from aiogram.filters import BaseFilter

from datetime import datetime, timedelta

from typing import List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger



from aiogram.filters.callback_data import CallbackData

from handlers import registration

import keyboards as kb

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


is_night = False

class NightFilter(BaseFilter):  
    async def __call__(self, message: Message) -> bool:
        return is_night

class DayFilter(BaseFilter):  
    async def __call__(self, message: Message) -> bool:
        return not is_night and registration.game_start


night_actions = []

night_callbacks = 0

voted_people = []

accused_people = {}



day = 1

apscheduler = AsyncIOScheduler()


    
night_router = Router(name = "night_router")
night_router.callback_query.filter(NightFilter())

day_router = Router(name = "day_router")
day_router.callback_query.filter(DayFilter())

class NightCallback(CallbackData, prefix = 'night'):
    user: int
    target: int
    action: str
    day: int


class VoteCallback(CallbackData, prefix = 'vote'):
    target: int
    day: int


class Player:
    action = "sleep"
    def __init__(self, user):
        self.id = user.id
        self.full_name = user.full_name
    def __str__(self):
        return f"{self.full_name}"
    async def sleep(self, bot: Bot):
        await bot.send_message(chat_id = self.id, text = "Чтобы заснуть нажмите на кнопку:",reply_markup = night_kb("sleep", self))

class Mafia(Player):
    action = "vote_kill"
    async def vote_kill(self, bot: Bot):
        await bot.send_message(chat_id = self.id, text = "Предложи кого убить:", reply_markup = night_kb(registration.live_players, self))

class Don(Player):
    action = "kill"
    async def kill(self, bot: Bot):
        await bot.send_message(chat_id = self.id, text = 'Выберите кого убить:', reply_markup = night_kb(registration.live_players, self))

class Doctor(Player):
    action = "heal"
    async def heal(self, bot: Bot):
        await bot.send_message(chat_id = self.id, text = 'Выберите кого вылечить:', reply_markup = night_kb(registration.live_players, self))
        
class Sheriff(Player):
    action = "check"
    async def check(self, bot: Bot):
        await bot.send_message(chat_id = self.id, text = 'Выбери кого проверить:', reply_markup = night_kb(registration.live_players, self))

class Maniac(Player):
    action = "murder"
    async def murder(self, bot: Bot):
         await bot.send_message(chat_id = self.id, text = 'Выбери кого зарезать:', reply_markup = night_kb(registration.live_players, self))

class Inspector(Player):
    action = "inspect"
    async def inspect(self, bot: Bot):
         await bot.send_message(chat_id = self.id, text = 'Выбери чью роль хочешь проверить:', reply_markup = night_kb(registration.live_players, self))

async def night_actions_result(night_actions: List[NightCallback], bot: Bot) -> None:
    """обработчик ночных действий"""
    night_actions.sort(key = lambda action: action.action, reverse = True)
    death_note = []
    for action in night_actions:
        user = next(filter(lambda player: player.id == action.target, registration.live_players))
        if action.action == 'kill' or action.action == 'murder':
            death_note.append(user)
        elif action.action == 'heal':
            if(user in death_note):
                death_note.remove(user)
    global day, is_night 
    day += 1
    is_night = False
    await bot.send_message(chat_id = registration.game_chat_id, text = f"Город просыпается🌞")
    await bot.set_chat_permissions(chat_id = registration.game_chat_id, permissions = ChatPermissions(can_send_messages = True))
    if len(death_note) == 1:
        registration.live_players.remove(death_note[0])
        await bot.send_message(chat_id = registration.game_chat_id, text = f"Сегодня ночью погиб <b>{death_note[0]}</b>.")
    elif len(death_note) == 2:
        registration.live_players.remove(death_note[0])
        registration.live_players.remove(death_note[1])
        await bot.send_message(chat_id = registration.game_chat_id, text = f"Сегодня ночью погибли <b>{death_note[0]}</b> и <b>{death_note[1]}</b>")
    night_actions.clear()
    match check_game_end(registration.live_players):
        case "mafia win":
            await bot.send_message(chat_id = registration.game_chat_id, text = f"Мафия победила!")
            return
        case "maniac win":
            await bot.send_message(chat_id = registration.game_chat_id, text = f"В городе никого не осталось. Маньяк хорошо сделал свою работу!")
            return
        case "peacful win":
            await bot.send_message(chat_id = registration.game_chat_id, text = f"Мирные жители выиграли")   
            return
        case "new don":
            await bot.send_message(chat_id = next(player for player in registration.live_players if isinstance(player, Don)).id, text = "Теперь ты новый <b>Дон</b>")
    msg = await bot.send_message(chat_id = registration.game_chat_id, text = f"Начинается обсуждение <b>{30*len(registration.live_players)}с!</b>\nВыбери кого ты считаешь <b>мафией</b>", reply_markup = vote_kb(registration.live_players))
    trigger = DateTrigger(run_date = datetime.now() + timedelta(seconds = 30*len(registration.live_players)))
    global job
    job = apscheduler.add_job(func = vote_process, trigger = trigger, args = [bot, msg])
    


def check_game_end(live_players: list):
    mafies_count = sum(1 for player in live_players if isinstance(player, Mafia) or isinstance(player, Don))
    peacful_count = sum(1 for player in live_players if not(isinstance(player, Mafia) or (isinstance(player, Don))))
    maniac_is_alive = Maniac in [type(player) for player in live_players]
    global is_night
    if mafies_count >= peacful_count and not maniac_is_alive:
        is_night = True
        registration.live_players.clear()
        registration.game_start = False
        registration.play_writed = False
        return "mafia win"
    elif mafies_count == 0 and not maniac_is_alive:
        is_night = True
        registration.live_players.clear()
        registration.game_start = False
        registration.play_writed = False
        return "peacful win"
    elif mafies_count == 0 and maniac_is_alive and peacful_count <= 1:
        is_night = True
        registration.live_players.clear()
        registration.game_start = False
        registration.play_writed = False
        return "maniac win"
    if sum(1 for player in live_players if isinstance(player, Don)) == 0 and mafies_count != 0:
        old_mafia = random.choice([player for player in live_players if isinstance(player, Mafia)])
        registration.live_players.remove(old_mafia)
        new_don = Don(user=type('User', (), {'id': old_mafia.id, 'full_name': old_mafia.full_name})())
        registration.live_players.append(new_don)
        return "new don"

async def vote_process(bot: Bot, msg: Message):
    global is_night, accused_people
    is_night = True
    if len(accused_people) != 0:
        if max(accused_people, key = accused_people.get) == 1:
            await msg.answer("Голосование пропущено")
        else:
            user = next(filter(lambda player: player.id == max(accused_people, key = accused_people.get), registration.live_players))
            registration.live_players.remove(user)
            await bot.send_message(chat_id = registration.game_chat_id,text = f"Выгоняем <b>{user}</b>")
    await bot.delete_message(chat_id = registration.game_chat_id, message_id = msg.message_id)    
    match check_game_end(registration.live_players):
        case "mafia win":
            await bot.send_message(chat_id = registration.game_chat_id, text = f"Мафия победила!")
            return
        case "maniac win":
            await bot.send_message(chat_id = registration.game_chat_id, text = f"В городе никого не осталось. Маньяк хорошо сделал свою работу!")
            return
        case "peacful win":
            await bot.send_message(chat_id = registration.game_chat_id, text = f"Мирные жители выиграли")   
            return
        case "new don":
            await bot.send_message(chat_id = next(player for player in registration.live_players if isinstance(player, Don)).id, text = "Теперь ты новый <b>Дон</b>")
    await bot.send_message(chat_id = registration.game_chat_id, text = "Город засыпает🌙", reply_markup = kb.go_to_bot_keyboard)
    await night_phase(registration.live_players, bot)

async def night_phase(live_players: list, bot: Bot) -> None:
    await bot.set_chat_permissions(chat_id = registration.game_chat_id, permissions = ChatPermissions(can_send_messages = False), use_independent_chat_permissions = True)
    global is_night
    is_night= True
    for player in live_players:
        player_type = type(player).__name__
        if player_type == 'Don':  
            await player.kill(bot)
        elif player_type == 'Mafia':
            await player.vote_kill(bot)
        elif player_type == 'Doctor':
            await player.heal(bot)
        elif player_type == 'Sheriff':
            await player.check(bot)
        elif player_type == 'Maniac':
            await player.kill(bot)
        elif player_type == 'Inspector':
            await player.inspect(bot)
        else:
            await player.sleep(bot)
    trigger = DateTrigger(run_date = datetime.now() + timedelta(seconds = 90))
    global job_night
    job_night= apscheduler.add_job(func = night_actions_result, trigger = trigger, args = [night_actions, bot])
    



def night_kb(players: list | str, executor: Player) -> InlineKeyboardMarkup:
    if isinstance(players, str):
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Уснуть😴', callback_data = NightCallback(user = 0, target = 0, action = 'sleep', day = day).pack())]])
    builder = InlineKeyboardBuilder()
    [builder.button(text = player.full_name, callback_data = NightCallback(user = executor.id, target = player.id, action = executor.action, day = day).pack()) for player in players]
    builder.adjust(1)
    return builder.as_markup()


def vote_kb(players: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    [builder.button(text = player.full_name, callback_data = VoteCallback(target = player.id, day = day).pack()) for player in players]
    builder.button(text = "пропуск", callback_data =  VoteCallback(target = 1, day = day).pack())
    builder.adjust(1)
    return builder.as_markup()


@day_router.message(DayFilter())
async def killed_filter(message: Message):
    if not list(filter(lambda player: player.id == message.from_user.id, registration.live_players)):
        await message.delete()
        print(registration.game_start)

# @day_router.callback_query()
# async def start_game(callback: CallbackQuery):
#     print(callback.data)
#     await callback.answer()

@day_router.callback_query(VoteCallback.filter())
async def vote_callback_handler(callback: CallbackQuery, callback_data: VoteCallback, bot: Bot):
    global accused_people
    if callback_data.day != day or not list(filter(lambda player: player.id == callback.from_user.id, registration.live_players)):
        callback.answer("ты по-моему перепутал")
        return
    if callback.from_user.id not in voted_people:
        if callback_data.target in accused_people:
            accused_people[callback_data.target] += 1
        else:
            accused_people[callback_data.target] = 1
        voted_people.append(callback.from_user.id)
        if callback_data.target == 1:
            await callback.message.answer(f"<b>{callback.from_user.full_name}</b> проголосовал за <b>пропуск</b>")
        else:
            await callback.message.answer(f"<b>{callback.from_user.full_name}</b> проголосовал за <b>{next(filter(lambda player: player.id == callback_data.target, registration.live_players))}</b>")
    if len(voted_people) == len(registration.live_players):
        apscheduler.remove_job(job_id = job.id)
        await vote_process(bot, callback.message)
        accused_people.clear()
        voted_people.clear()
    await callback.answer("Твой голос учтен")

    
@night_router.callback_query(NightCallback.filter())
async def night_actions_handler(callback: CallbackQuery, callback_data: NightCallback, bot: Bot):
    if callback_data.day != day:
        await callback.answer("ты по-моему перепутал")
        return
    global night_actions, night_callbacks
    if callback_data.action == 'vote_kill':
        await bot.send_message(chat_id = next(filter(lambda player: type(player).__name__ == 'Don', registration.live_players)).id, text = f"<b>{callback.from_user.full_name}</b> предлагает убить <b>{next(filter(lambda player: player.id == callback_data.target, registration.live_players))}</b>")
    elif callback_data.action == 'kill':
        night_actions.append(callback_data)
        await callback.message.answer(f"Вы решили убить <b>{next(filter(lambda player: player.id == callback_data.target, registration.live_players))}</b>")
        for player in filter(lambda player: type(player).__name__ == 'Mafia', registration.live_players):
            await bot.send_message(chat_id = player.id, text = f"<b>Дон</b> выбрал<b> {next(filter(lambda player: player.id == callback_data.target, registration.live_players))}</b> в качестве жертвы")
    elif callback_data.action == 'heal':
        night_actions.append(callback_data)
        await callback.message.answer(f"Лечим <b>{next(filter(lambda player: player.id == callback_data.target, registration.live_players))}</b>")
    elif callback_data.action == 'check':
        if type(next(filter(lambda player: player.id == callback_data.target, registration.live_players))) == Mafia or  type(next(filter(lambda player: player.id == callback_data.target, registration.live_players))) == Don:
            await callback.message.answer(f"<b>{next(filter(lambda player: player.id == callback_data.target, registration.live_players))}</b> является членом мафии")
        else:
            await callback.message.answer(f"<b>{next(filter(lambda player: player.id == callback_data.target, registration.live_players))}</b> не является членом мафии")
    elif callback_data.action == 'murder':
        night_actions.append(callback_data)
        await callback.message.answer(text = f"Вы решили убить<b>{next(filter(lambda player: player.id == callback_data.target, registration.live_players))}</b>")
        await bot.send_message(chat_id = callback_data.target, text = "Тебя заткнула <b>ночная бабочка</b> этот день ты будешь молчать! А так же не имеешь права голосовать")
    elif callback_data.action == 'inspect':
        if type(next(filter(lambda player: player.id == callback_data.target, registration.live_players))) != Player:
            await callback.message.answer(f"У игрока <b>{next(filter(lambda player: player.id == callback_data.target, registration.live_players))}</b> активная роль(<em>не мирный житель</em>)")
        else:
            await callback.message.answer(f"Игрок <b>{next(filter(lambda player: player.id == callback_data.target, registration.live_players))}</b> мирный житель")
    await callback.message.delete()
    night_callbacks += 1
    if(night_callbacks == len(registration.live_players)):
        apscheduler.reschedule_job(job_id = job_night.id, trigger = 'date', run_date = datetime.now())
        night_callbacks = 0
    await callback.answer()
    await callback.message.answer("Вернуться в беседу", reply_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = "Перейти в беседу", url = "https://t.me/kursa4mafia")]]))