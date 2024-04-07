import time
import random
import json
import requests_system

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from Configuration.bot_config import bot
import db
from AI.ai_manager import recommendation_generator
from states import Recommendation, Authorize, MovieSearch, FilterSteps
from ui_elements import *

router = Router()


# --------- COMMANDS ----------------------------------
# Command /start
@router.message(Command("start"))
@router.message(Command("login"))
async def cmd_start(message: types.Message, state: FSMContext):
    greeting = f"Welcome, {message.from_user.first_name}!"
    await message.reply(greeting)
    # a basic keyboard in the start menu
    await auth(message.from_user.id, state)

# Command /help
@router.message(Command("help"))
async def help_command(message: types.Message):
    greeting = f"Hey there, {message.from_user.first_name}!"

    commands = [
        "/start - Start Cinemate",
        "/help - Get help",
        "/name_search - Search by name",
        "/filter_search - Search by criteria",
        "/recommend - Get recommendation",
        "/my_movielist - My movielist"
    ]

    help_message = f"{greeting}\n\nHere are the available commands:\n"
    help_message += "\n".join(commands)
    await message.reply(help_message)

# Command /name_search
@router.message(Command("name_search"))
@router.message(StateFilter(None), F.text == 'Search by name')
async def search_by_name(message: types.Message, state: FSMContext):
    await message.reply("Please enter a title of the movie.")
    await state.set_state(MovieSearch.wait_movie_name)

@router.message(StateFilter(MovieSearch.wait_movie_name))
async def process_movie_name(message: types.Message, state: FSMContext):
    movie_name = message.text

    response = await requests_system.get_movies_by_title(movie_name,1)

    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            movie_info = data["results"][0]

            movie_message = f"Movie '{movie_info['title']}' is found!"

            keyboard = get_movie_by_name_info_keyboard(movie_info['id'])

            await message.reply(movie_message, reply_markup=keyboard)
        else:
            await message.reply(f"No movie found with the name '{movie_name}'.")
    else:
        await message.reply("Error occurred while searching for the movie.")
    await state.set_state(None)

#<----> HANDLERS FOR SEARCH BY MOVIE TITLE

# Handle callback queries for movie INFORMATION
@router.callback_query(F.data.startswith("info_"))
async def handle_movie_info(callback: types.CallbackQuery):
    movie_id = callback.data.split("_")[1]

    response = await requests_system.get_movie_by_id(movie_id)

    if response.status_code == 200:
        movie_info = response.json()

        info_message = f"Title: {movie_info['title']}\n" \
                       f"Movie for adults: {'Yes' if movie_info['adult'] else 'No'}\n" \
                       f"Original language: {movie_info['original_language']}\n" \
                       f"Release date: {movie_info['release_date']}\n" \
                       f"Popularity: {movie_info['popularity']}\n" \
                       f"Average voting score: {movie_info['vote_average']}"

        await callback.message.answer(info_message)
    else:
        await callback.message.answer("Error occurred while retrieving movie information.")


# Handle callback queries for RATING THE MOVIE
@router.callback_query(F.data.startswith("rate_movie"))
async def rate_movie(callback: types.CallbackQuery, state: FSMContext):
    movie_id = callback.data.split("_")[2]
    user_id = callback.from_user.id

    response = await requests_system.get_movie_list(user_id=user_id)
    if response.status_code == 200:
        movie_list = response.json()
        movie_ids = [movie['id'] for movie in movie_list]
        if int(movie_id) not in movie_ids:
            await callback.answer("You can only rate movies that are in your movie list.")
            return

    await callback.message.answer("Please enter your rating for this movie (1-10):")
    await state.set_state(MovieSearch.wait_rate)
    await state.update_data(movie_id=movie_id)


@router.message(StateFilter(MovieSearch.wait_rate))
async def handle_rating(message: types.Message, state: FSMContext):
    rating = message.text

    try:
        rating = int(rating)
        if rating < 1 or rating > 10:
            raise ValueError
    except ValueError:
        await message.answer("Invalid rating. Please enter a number between 1 and 10.")
        return

    state_data = await state.get_data()
    movie_id = state_data.get("movie_id")

    response = await requests_system.rate_movie_from_list(user_id=message.from_user.id, movie_id=movie_id, score=rating)

    if response.status_code == 200:
        await message.answer("Rating submitted successfully!")
    else:
        await message.answer("Failed to submit rating. Please try again later.")

    await state.set_state(None)

# Handle callback queries for ADD TO MOVIELIST
@router.callback_query(F.data.startswith("add_to_movielist"))
async def add_to_movielist(callback: types.CallbackQuery, state: FSMContext):
    movie_id = callback.data.split('_')[3]
    user_id = callback.from_user.id

    response = await requests_system.add_movie_to_list(user_id, movie_id)

    if response is not None and response.status_code == 200:
        await callback.answer("Movie successfully added to movielist.")
    else:
        await callback.answer("Failed to add the movie to movielist. Please try again later.")

# Handle callback queries ADD TO FAVORITE
@router.callback_query(F.data.startswith("add_to_favorite"))
async def add_to_favorite(callback: types.CallbackQuery, state: FSMContext):
    movie_id = callback.data.split("_")[3]

    response = await requests_system.get_movie_list(user_id=callback.from_user.id)
    if response.status_code == 200:
        movielist = response.json()
        if any(movie["id"] == int(movie_id) for movie in movielist):
            response_favorite = await requests_system.set_favorite_movie_from_list(user_id=callback.from_user.id,
                                                                                    movie_id=movie_id,
                                                                                    is_favorite=True)
            if response_favorite.status_code == 200:
                await callback.answer("Added to favourites")
            else:
                await callback.answer("Failed to add to favourites. Please try again later.")
        else:
            await callback.answer("You can't add to favorites a movie that is not in your movielist.")
    else:
        await callback.answer("Failed to fetch your movielist. Please try again later.")

# Handle callback queries for movie OVERVIEW
@router.callback_query(F.data.startswith("overview_"))
async def handle_movie_overview(callback: types.CallbackQuery):
    movie_id = callback.data.split("_")[1]

    response = await requests_system.get_movie_by_id(movie_id)

    if response.status_code == 200:
        movie_info = response.json()

        await callback.message.answer(f"Overview: {movie_info['overview']}")
    else:
        await callback.message.answer("Error occurred while retrieving movie overview.")

# Handle callback queries for movie GENRES
@router.callback_query(F.data.startswith("genres_"))
async def handle_movie_genres(callback: types.CallbackQuery):
    movie_id = callback.data.split("_")[1]

    response = await requests_system.get_movie_by_id(movie_id)

    if response.status_code == 200:
        movie_info = response.json()

        genres = [genre['name'] for genre in movie_info['genres']]

        await callback.message.answer(f"Genres: {', '.join(genres)}")
    else:
        await callback.message.answer("Error occurred while retrieving movie genres.")


# Handle callback queries for DELETE FROM MOVIELIST
@router.callback_query(F.data.startswith("delete_from_movielist"))
async def delete_from_movielist(callback: types.CallbackQuery, state: FSMContext):
    movie_id = callback.data.split("_")[3]
    user_id = callback.from_user.id

    try:
        movie_id = int(movie_id)
    except ValueError:
        await callback.answer("Invalid movie ID.")
        return

    response = await requests_system.get_movie_list(user_id=user_id)
    if response.status_code == 200:
        movie_list = response.json()
        movie_ids = [movie['id'] for movie in movie_list]
        if movie_id not in movie_ids:
            await callback.answer("The movie is not in the list.")
            return

    response = await requests_system.remove_movie_to_list(user_id=user_id, movie_id=movie_id)
    if response.status_code == 200:
        await callback.answer("Movie removed from your movie list.")
    else:
        await callback.answer("Failed to remove movie from your movie list. Please try again later.")


#HANDLERS FOR SEARCH BY MOVIE TITLE END <---->


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
        await process_rec_movielist_request(callback.message)
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
            await process_rec_movielist_request(callback.message)


# Handle navigation
@router.callback_query(F.data.startswith("back_"))
async def callbacks_num(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]

    if action == "main":
        await callback.message.answer("Hi there, choose what you wanna do by pressing a button",
                                      reply_markup=get_start_menu())
    elif action == "recommend":
        await get_recommendation(callback.message)


# ----- REGISTER HANDLE NEXT STEPS ------
# Handle recommendation states
# Handle similarity request
@router.message(Recommendation.similarity_request)
async def process_rec_similarity_request(message: types.Message, state: FSMContext):
    await state.get_data()
    film_name = message.text
    await message.reply("Wait, please")
    res = await recommendation_generator('similarity', film_name)
    await message.answer(res, reply_markup=get_recommendation_additional_menu('similarity'))
    await state.clear()


# Handle expectation request
@router.message(Recommendation.expectation_request)
async def process_rec_expectation_request(message: types.Message, state: FSMContext):
    await state.get_data()
    film_name = message.text
    await message.reply("Wait, please")
    res = await recommendation_generator('expectations', film_name)
    await message.answer(res, reply_markup=get_recommendation_additional_menu('expectations'))
    await state.clear()


# Handle recommendation due to movielist request
async def process_rec_movielist_request(message: types.Message):
    response = await requests_system.get_movie_list(user_id=message.chat.id)
    if response == "[]":
        await message.answer("Ohh... Your movielist is empty",
                             reply_markup=get_recommendation_additional_menu('movielist'))
    else:
        res = json.loads(response.text)
        if len(res) == 0:
            await message.answer("Ohh... Your movielist is empty",
                                 reply_markup=get_recommendation_additional_menu('movielist'))
        else:
            titles = ""
            for r in res:
                titles += r["original_title"] + "; "
            res = await recommendation_generator('movielist', titles)
            await message.answer(res, reply_markup=get_recommendation_additional_menu('movielist'))


async def auth(chatID: str, state: FSMContext):
    await bot.send_message(chatID, "Please, sign up!\nEnter your email:")
    await state.set_state(Authorize.wait_email)


@router.message(Authorize.wait_email)
async def email_sent(message: types.Message, state: FSMContext):
    response = await requests_system.sign_in_otp(message.text)

    if response.status_code == 200:
        await db.set_user_email(message.from_user.id, message.text)
        await state.set_state(Authorize.wait_otp)
        await bot.send_message(message.from_user.id,
                               "A one-time login code password has been sent to the given e-mail address. "
                               "Please enter it:")
    else:
        await state.clear()
        await bot.send_message(message.from_user.id,
                               "Error")


@router.message(Authorize.wait_otp)
async def otp_sent(message: types.Message, state: FSMContext):
    await message.answer("Wait, please")
    email = await db.get_user_email(message.from_user.id)
    response = await requests_system.verify_otp(email, message.text)
    if response.status_code == 200:
        data = response.json()
        access_token = data.get('accessToken')
        refresh_token = data.get('refreshToken')
        await db.set_access_token(message.from_user.id, access_token)
        await db.set_refresh_token(message.from_user.id, refresh_token)
        await bot.send_message(message.from_user.id, "Login successful")
    else:
        await bot.send_message(message.from_user.id, "Login unsuccessful")
        await db.set_user_email(message.from_user.id, "")
    await state.clear()


@router.message(Command("my_movielist"))
@router.message(StateFilter(None), F.text == 'My movielist')
async def my_movielist(message: types.Message):
    if not await db.user_and_token_exist(message.from_user.id):
        await requests_system.user_unauthorized(message.from_user.id)
        return

    response = await requests_system.get_movie_list(user_id=message.from_user.id)

    if response.status_code == 200:
        movie_list = response.json()
        if movie_list:
            movie_info_list = []
            for movie in movie_list:
                movie_info = movie["original_title"]
                if movie["score"] is not None:
                    movie_info += f", your score: {movie['score']}"
                if movie["is_favorite"]:
                    movie_info += " ❤️"
                movie_info_list.append(movie_info)
            movie_info_text = "\n".join(movie_info_list)
            await message.reply(movie_info_text)
        else:
            await message.reply("Your movie list is empty.")
    else:
        await message.reply("Error occurred while fetching your movie list.")

@router.message(Command("add"))
async def add_movie_to_list(message: types.Message):
    args = message.text.split(' ')
    movie_id = args[1]
    response = await requests_system.add_movie_to_list(user_id=message.from_user.id, movie_id=movie_id)
    await message.reply(f"Status code = {response.status_code}.\n{response.text}")


@router.message(Command("remove"))
async def remove_movie_to_list(message: types.Message):
    args = message.text.split(' ')
    movie_id = args[1]
    response = await requests_system.remove_movie_to_list(user_id=message.from_user.id, movie_id=movie_id)
    await message.reply(f"Status code = {response.status_code}.\n{response.text}")


@router.message(Command("rate"))
async def rate_movie_from_list(message: types.Message):
    args = message.text.split(' ')
    movie_id = args[1]
    score = args[2]
    response = await requests_system.rate_movie_from_list(user_id=message.from_user.id, movie_id=movie_id, score=score)
    await message.reply(f"Status code = {response.status_code}.\n{response.text}")


@router.message(Command("fav"))
async def remove_movie_to_list(message: types.Message):
    args = message.text.split(' ')
    movie_id = args[1]
    is_favorite = args[2]
    response = await requests_system.set_favorite_movie_from_list(user_id=message.from_user.id, movie_id=movie_id,
                                                                  is_favorite=is_favorite)
    await message.reply(f"Status code = {response.status_code}.\n{response.text}")


@router.message(Command("title"))
async def get_movies_by_title(message: types.Message):
    args = message.text.split(' ')
    title = args[1]
    page = args[2]
    response = await requests_system.get_movies_by_title(title=title, page=page)
    await message.reply(f"Status code = {response.status_code}.\n{response.text[:4000]}")


@router.message(Command("filter_search"))
@router.message(StateFilter(None), F.text == 'Search by criteria')
async def get_movies_by_filters(message: types.Message, state: FSMContext):
    await message.answer(
        text="Enter year:"
    )
    await state.set_state(FilterSteps.handle_year)


@router.message(FilterSteps.handle_year)
async def get_filter_year(message: types.Message, state: FSMContext):
    await state.update_data(chosen_year=message.text)
    response_genre = await requests_system.get_genres() 
    all_genres = json.loads(response_genre.text)
    joined_genres = ", ".join(list(map(lambda x: x["name"],all_genres)))
    await message.answer(
        text=f"Enter genre from the list below:\n\n{joined_genres}"
    )
    await state.set_state(FilterSteps.handle_genre)


@router.message(FilterSteps.handle_genre)
async def get_filter_genre(message: types.Message, state: FSMContext):
    response_genre = await requests_system.get_genres() 
    all_genres = json.loads(response_genre.text)
    selected_genre = list(filter(lambda x: x["name"] == message.text,all_genres))
    joined_genres = ", ".join(list(map(lambda x: x["name"],all_genres)))
    selected_genre_id = None
    if len(selected_genre) > 0:
        selected_genre_id = selected_genre[0]["id"]
    else:
        await message.answer(
            text=f"Genre {message.text} not found.\n\nPlease enter genre from the list below:\n\n{joined_genres}"
        )
        return

    await state.update_data(chosen_genre=[selected_genre_id])

    filter_data = await state.get_data()
    await message.answer(
        text=f"You have chose {filter_data['chosen_year']}, {message.text}"
    )
    response = await requests_system.get_movies_by_filters(1, year = filter_data['chosen_year'], genres = filter_data['chosen_genre']) 
    movie_list = json.loads(response.text)["results"]
    for mov in movie_list:
        await message.answer(f"Title: <b>{mov['title']}</b> ({mov['release_date']})\n"
                             f"Genre: {",".join(list(map(lambda x: x['name'], mov['genres'])))}\n"
                             f"Overview: {mov['overview']}", parse_mode="HTML")
    
    if len(movie_list) == 0:
        await message.answer("No movies found.")

    await state.clear()


@router.message(Command("movie"))
async def get_movies_by_title(message: types.Message):
    args = message.text.split(' ')
    movie_id = args[1]
    response = await requests_system.get_movie_by_id(movie_id)
    await message.reply(f"Status code = {response.status_code}.\n{response.text}")


@router.message(Command("genres"))
async def get_genres(message: types.Message):
    response = await requests_system.get_genres()
    await message.reply(f"Status code = {response.status_code}.\n{response.text}")


@router.message(Command("genresid"))
async def get_genres(message: types.Message):
    args = message.text.split(' ')
    genres_id = args[1]
    response = await requests_system.get_genres_by_id(genres_id)
    await message.reply(f"Status code = {response.status_code}.\n{response.text}")


@router.message(Command("sign_out"))
async def sign_out(message: types.Message):
    response = await requests_system.sign_out(user_id=message.from_user.id)
    await message.reply(f"Status code = {response.status_code}.\n{response.text}")


@router.message(Command("clean_user"))
async def sign_out(message: types.Message):
    await db.delete_user(message.from_user.id)
    await message.reply("User deleted")


@router.message(Command("break_token"))
async def sign_out(message: types.Message):
    await db.set_access_token(message.from_user.id, "eyJhbGciOiJIUzI1NasddaspZCI6Im14c3dUYUE4RzZxUjk0b2QiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJasdasdasdaWNhdGVkIiwiZXhwIjoxNzEyODc5MjE2LCJpYXQiOjE3MTIyNzQ0MTasdasdayI6Imh0dHBzOi8veW9zbnZ4dm1lbGZkbGN1b3pkeHguc3VwYWJhc2UuY28vYXV0aC92MSIsInN1YiI6IasdasdaZmI0LTNhOTgtNDdkMi05MTFiLWY0NjA2YmM1MDU2ZCIsImVtYasdasdicG96aGFyb3YyMDAzQGdtYWlsLmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzasdasdV0YWRhdGEiOnsiZW1haWwiOiJwb3poYXJvdjIwMDNAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJwaG9uZV9sadasdasdZCI6ZmFsc2UsInNwaWNpZmljRmllbGRzIjoidmFsdWUiLCJzdWIiOiJmMDQ3ZGZiNC0zYTk4LTQ3ZDItOTExYi1mNDYwNmJjNTAasdasdasdcm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJvdHAiLCJ0aWasd3RhbXAiOjE3MTIyNzQ0MTZ9XSwic2Vzc2lvbl9pZCI6ImU3Y2FiOTkxLTk0ZjAtNDY2My05NmNiLTg4ZDkzNTcxZjIzYyIsImlzX2Fub255basdasd6ZmFsc2V9.-oFmOMHSsI2dxOiR3UMDasdasdM-bWPA_HlasdcBtzo")
    await message.reply("Token is broken")

