import time
import random

import db
import requests_system

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from Configuration.bot_config import bot
from AI.ai_manager import recommendation_generator
from states import Recommendation
from states import Authorize

from ui_elements import *

router = Router()


# --------- COMMANDS ----------------------------------
# Command /start
@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    # a basic keyboard in the start menu
    # await message.answer("Hello!", reply_markup=get_start_menu())
    await auth(message.from_user.id, state)


# Handle input text (including ReplyKeyboardMarkup button was pressed)
# Handle Command /recommend OR recommendation button was pressed
@router.message(Command("recommend"))
@router.message(StateFilter(None), F.text == 'Recommend me')
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
        await state.set_state(Recommendation.similarity_request)
    if action == "expectation":
        await callback.message.answer("Write some expectations for the film")
        # register next step handler with state
        await state.set_state(Recommendation.expectation_request)


# ----- REGISTER HANDLE NEXT STEPS ------
# Handle recommendation states
# Handle similarity request
@router.message(Recommendation.similarity_request)
async def process_request(message: types.Message, state: FSMContext):
    await state.get_data()
    film_name = message.text
    await message.reply("Wait, please")
    res = await recommendation_generator('similarity', film_name)
    await message.answer(res)
    await state.clear()


# Handle expectation request
@router.message(Recommendation.expectation_request)
async def process_request(message: types.Message, state: FSMContext):
    await state.get_data()
    film_name = message.text
    await message.reply("Wait, please")
    res = await recommendation_generator('expectations', film_name)
    await message.answer(res)
    await state.clear()


async def auth(chatID: str, state: FSMContext):
    await bot.send_message(chatID, "Please, sign up!\nEnter your email:")
    await state.set_state(Authorize.wait_email)


@router.message(Authorize.wait_email)
async def email_sent(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id,
                           "A one-time login code password has been sent to the given e-mail address. Please enter it:")
    response = await requests_system.sign_in_otp(message.text)

    if response.status_code == 200:
        await db.set_user_email(message.from_user.id, message.text)
        print(f"set email {message.from_user.id}  {message.text}")
        await state.set_state(Authorize.wait_otp)
    else:
        await state.clear()


@router.message(Authorize.wait_otp)
async def otp_sent(message: types.Message, state: FSMContext):
    await message.answer("Wait, please")
    print(f"get email {message.from_user.id}")
    email = await db.get_user_email(message.from_user.id)
    print(f"get email = {email}")

    response = await requests_system.verify_otp(email, message.text)

    if response.status_code == 200:
        # set token
        await bot.send_message(message.from_user.id, "Login successful")
    else:
        await bot.send_message(message.from_user.id, "Login unsuccessful")
    await state.clear()
