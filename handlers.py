import time
import random
import requests_system

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from Configuration.bot_config import bot
from states import Recommendation
from ui_elements import *

router = Router()


# --------- COMMANDS ----------------------------------
# Command /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    # a basic keyboard in the start menu
    await message.answer("Hello!", reply_markup=get_start_menu())


# Handle input text (including ReplyKeyboardMarkup button was pressed)
# Handle Command /recommend OR recommendation button was pressed
@router.message(Command("recommend"))
@router.message(F.text == 'Recommend me')
async def get_recommendation(message: types.Message):
    await message.answer("Choose what you wanna do", reply_markup=get_recommendation_main_menu())


# ----- CALLBACK PROCESSING -------
# Handle recommendation callbacks
@router.callback_query(F.data.startswith("recommendation_"))
async def callbacks_num(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]
    if action == "movielist":
        await callback.message.answer("Due to your movielist")
    elif action == "similarity":
        await callback.message.answer("Write a name of the film similar to the future recommendation")
        # register next step handler with state
        await state.set_state(Recommendation.message_request)
    if action == "expectation":
        await callback.message.answer("Write some expectations for the film")
        # register next step handler with state
        await state.set_state(Recommendation.message_request)


# ----- REGISTER HANDLE NEXT STEPS ------
# Handle recommendation states
@router.message(Recommendation.message_request)
async def process_request(message: types.Message, state: FSMContext):
    await state.get_data()
    print(message.text)
    await state.clear()


@router.message(Command("test"))
async def test1(message: types.Message):
    await requests_system.sign_in("test2@test.com")
