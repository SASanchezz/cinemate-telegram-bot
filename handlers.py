import time
import random
import requests_system

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from Configuration.bot_config import bot
from AI.ai_manager import recommendation_generator
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
    await message.answer(res, reply_markup=get_recommendation_additional_menu('similarity'))
    await state.clear()


@router.message(Command("test"))
async def test1(message: types.Message):
    await requests_system.sign_in("test2@test.com")
