import time
import random
import requests_system

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from Configuration.bot_config import bot
import db
from AI.ai_manager import recommendation_generator
from states import Recommendation, Authorize
from ui_elements import *

router = Router()


# --------- COMMANDS ----------------------------------
# Command /start
@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    # a basic keyboard in the start menu
    await requests_system.auth(message.from_user.id, state)


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
        await callback.message.answer("Wait please, I am analysing your movielist")
        # register next step handler with state
        await state.set_state(Recommendation.movielist_request)
    elif action == "similarity":
        await callback.message.answer("Write a name of the film similar to the future recommendation")
        # register next step handler with state
        await state.set_state(Recommendation.similarity_request)
    elif action == "expectation":
        await callback.message.answer("Write some expectations for the film")
        # register next step handler with state
        await state.set_state(Recommendation.expectation_request)

    elif action == "regenerate":
        recommend_type = callback.data.split("_")[2]
        if recommend_type == "similarity":
            await callback.message.answer("Write a name of the film similar to the future recommendation")
            await state.set_state(Recommendation.similarity_request)
        elif recommend_type == "expectations":
            await callback.message.answer("Write some expectations for the film")
            # register next step handler with state
            await state.set_state(Recommendation.expectation_request)
        else:
            await callback.message.answer("Wait please, I am analysing your movielist")
            # register next step handler with state
            await state.set_state(Recommendation.movielist_request)


# Handle navigation
@router.callback_query(F.data.startswith("back_"))
async def callbacks_num(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]

    if action == "main":
        await callback.message.answer("Welcome there, choose what you wanna do by pressing a button", reply_markup=get_start_menu())
    elif action == "recommend":
        await get_recommendation(callback.message)


# ----- REGISTER HANDLE NEXT STEPS ------
# Handle recommendation states
# Handle similarity request
@router.message(Recommendation.similarity_request)
async def process_request(message: types.Message, state: FSMContext):
    await state.get_data()
    film_name = message.text
    await message.reply("Wait, please")
    res = await recommendation_generator('similarity', film_name)
    await message.answer(res, reply_markup=get_recommendation_additional_menu('similarity'))
    await state.clear()


# Handle expectation request
@router.message(Recommendation.expectation_request)
async def process_request(message: types.Message, state: FSMContext):
    await state.get_data()
    film_name = message.text
    await message.reply("Wait, please")
    res = await recommendation_generator('expectations', film_name)
    await message.answer(res, reply_markup=get_recommendation_additional_menu('expectations'))
    await state.clear()


# Handle expectation request
@router.message(Recommendation.movielist_request)
async def process_request(message: types.Message, state: FSMContext):
    await state.get_data()
    film_name = message.text
    res = await recommendation_generator('movielist', film_name)
    await message.answer(res, reply_markup=get_recommendation_additional_menu('movielist'))
    await state.clear()





@router.message(Authorize.wait_email)
async def email_sent(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id,
                           "A one-time login code password has been sent to the given e-mail address. Please enter it:")
    response = await requests_system.sign_in_otp(message.text)

    if response.status_code == 200:
        await db.set_user_email(message.from_user.id, message.text)
        await state.set_state(Authorize.wait_otp)
    else:
        await state.clear()


@router.message(Authorize.wait_otp)
async def otp_sent(message: types.Message, state: FSMContext):
    await message.answer("Wait, please")
    email = await db.get_user_email(message.from_user.id)
    response = await requests_system.verify_otp(email, message.text)
    print(response.text)
    if response.status_code == 200:
        # set token
        await bot.send_message(message.from_user.id, "Login successful")
    else:
        await bot.send_message(message.from_user.id, "Login unsuccessful")
    await state.clear()

