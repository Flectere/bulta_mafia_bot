from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery

from aiogram.types.chat_permissions import ChatPermissions

from handlers import registration

from callbacks import game_process

import keyboards as kb

game_settings_router = Router()

count_roles = 0

count_mafies = 0
count_sheriffs = 0
count_doctors = 0

active_roles = []

roles = ['mafia','don', 'doctor', 'sheriff', 'peaceful man', 'night butterfly', 'maniac', 'inspector']

config_roles = {1: [roles[1]],
                2: [roles[1], roles[2]], 
                3: [roles[1], roles[2], roles[3]], 
                4: [roles[1], roles[2], roles[3], roles[4]],
                5: [roles[1], roles[2], roles[3], roles[4], roles[4]],
                6: [roles[1], roles[0], roles[2], roles[3], roles[4], roles[4]], 
                7: [roles[1], roles[0], roles[2], roles[3], roles[4], roles[4], roles[4]], 
                8: [roles[1], roles[0], roles[2], roles[3], roles[4], roles[4], roles[4], roles[5]],
                9: [roles[1], roles[0], roles[2], roles[3], roles[4], roles[4], roles[4], roles[4], roles[5]], 
                10: [roles[1], roles[0], roles[2], roles[3], roles[4], roles[4], roles[4], roles[4], roles[5], roles[6]],
                11: [roles[1], roles[0], roles[2], roles[3], roles[4], roles[4], roles[4], roles[4], roles[4], roles[5], roles[6]], 
                12: [roles[1], roles[0], roles[0], roles[2], roles[3], roles[4], roles[4], roles[4], roles[4], roles[4], roles[5], roles[6]], 
                13: [roles[1], roles[0], roles[0], roles[2], roles[3], roles[4], roles[4], roles[4], roles[4], roles[4], roles[5], roles[6], roles[7]], 
                14: [roles[1], roles[0], roles[0], roles[2], roles[3], roles[4], roles[4], roles[4], roles[4], roles[4], roles[4], roles[5], roles[6], roles[7]]}


def save_roles():
    """сохраняет списки ролей"""
    global count_mafies
    global count_doctors
    global count_sheriffs
    global active_roles
    for _ in range(count_mafies):
        active_roles.append(roles[0])
    for _ in range(count_doctors):
        active_roles.append(roles[2])
    for _ in range(count_sheriffs):
        active_roles.append(roles[3])
    if len(active_roles) == 0:
        active_roles = config_roles[len(registration.active_users)].copy()


@game_settings_router.callback_query(F.data == 'manual_settings')
async def settings_game(callback: CallbackQuery):
    await callback.message.edit_text("Настройки ролей:",reply_markup = kb.manual_role_settings_keyboard)
    await callback.answer()


@game_settings_router.callback_query(F.data == 'save_settings')
async def save_changes(callback:CallbackQuery):
    await callback.message.edit_text("Выбор настроек:", reply_markup = kb.select_settings_keyboard)


@game_settings_router.callback_query(F.data == 'start_game')
async def start_game(callback: CallbackQuery, bot: Bot):
    await callback.message.answer("Город засыпает🌙", reply_markup = kb.go_to_bot_keyboard)
    save_roles()
    await callback.message.delete()
    await registration.role_distribution(bot)
    await game_process.night_phase(live_players = registration.live_players, bot = bot)
    await bot.set_chat_permissions(registration.game_chat_id, ChatPermissions(can_send_messages = False))
    registration.registration_start = False
    registration.game_start = True
    

@game_settings_router.callback_query(F.data == 'edit_mafia')
async def edit_mafia_count(callback:CallbackQuery):
    await callback.message.edit_text(f"Количество мафий: {count_mafies}",reply_markup=kb.edit_mafia_keyboard)
    await callback.answer()

@game_settings_router.callback_query(F.data == "plus_mafia")
async def plus_mafia_func(callback:CallbackQuery):
    global count_mafies
    global count_roles
    if count_roles >= len(registration.active_users):
        await callback.answer("ПРЕВЫШЕНО ДОПУСТИМОЕ КОЛИЧЕСТВО РОЛЕЙ 😡")   
        return
    count_roles += 1
    count_mafies += 1
    await callback.message.edit_text(f"Количество мафий: {count_mafies}", reply_markup = kb.edit_mafia_keyboard)
    await callback.answer()

@game_settings_router.callback_query(F.data == "minus_mafia")
async def minus_mafia_func(callback:CallbackQuery):
    global count_mafies
    if count_mafies <= 0:
        await callback.answer()   
        return
    count_mafies -= 1
    await callback.message.edit_text(f"Количество мафий: {count_mafies}", reply_markup = kb.edit_mafia_keyboard)
    await callback.answer()


@game_settings_router.callback_query(F.data == 'edit_doctor')
async def edit_doctor_count(callback:CallbackQuery):
    await callback.message.edit_text(f"Количество докторов: {count_doctors}",reply_markup=kb.edit_doctor_keyboard)
    await callback.answer()

@game_settings_router.callback_query(F.data == "plus_doctor")
async def plus_doctor_func(callback:CallbackQuery):
    global count_doctors
    global count_roles
    if count_roles>=len(registration.active_users):
        await callback.answer("ПРЕВЫШЕНО ДОПУСТИМОЕ КОЛИЧЕСТВО РОЛЕЙ 😡")   
        return 
    count_roles += 1
    count_doctors += 1
    await callback.message.edit_text(f"Количество докторов: {count_doctors}",reply_markup=kb.edit_doctor_keyboard)
    await callback.answer()

@game_settings_router.callback_query(F.data == "minus_doctor")
async def minus_doctor_func(callback:CallbackQuery):
    global count_doctors
    global count_roles
    if count_doctors <= 0:
        await callback.answer()
        return
    count_roles -= 1
    count_doctors -= 1
    await callback.message.edit_text(f"Количество докторов: {count_doctors}",reply_markup=kb.edit_doctor_keyboard)
    await callback.answer()   


@game_settings_router.callback_query(F.data == 'edit_sheriff')
async def edit_sheriff_count(callback:CallbackQuery):
    await callback.message.edit_text(f"Количество комиссаров: {count_sheriffs}",reply_markup=kb.edit_sheriff_keyboard)
    await callback.answer()

@game_settings_router.callback_query(F.data == "plus_sheriff")
async def plus_sheriff_func(callback:CallbackQuery):
    global count_sheriffs
    global count_roles
    if count_roles>=len(registration.active_users):
        await callback.answer("ПРЕВЫШЕНО ДОПУСТИМОЕ КОЛИЧЕСТВО РОЛЕЙ 😡")   
        return 
    count_roles += 1
    count_sheriffs += 1
    await callback.message.edit_text(f"Количество комиссаров: {count_sheriffs}",reply_markup=kb.edit_sheriff_keyboard)
    await callback.answer()    

@game_settings_router.callback_query(F.data == "minus_sheriff")
async def minus_sheriff_func(callback:CallbackQuery):
    global count_sheriffs
    if count_sheriffs <= 0:
        await callback.answer()   
        return
    count_sheriffs -= 1
    await callback.message.edit_text(f"Количество комиссаров: {count_sheriffs}",reply_markup=kb.edit_sheriff_keyboard)
    await callback.answer()   


@game_settings_router.callback_query(F.data == "go_back")
async def go_back_func(callback:CallbackQuery):
    await callback.message.edit_text(f"Настройки игры:", reply_markup = kb.manual_role_settings_keyboard)
    await callback.answer()