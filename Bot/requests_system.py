import json

import requests
import db
from Configuration.bot_config import bot

api_base_url = "https://cinemate.space/api/v1"


async def send_request(request: requests.Request) -> requests.Response:
    data = request.json
    if data:
        if 'accessToken' in data:
            if data["accessToken"] == "":
                pass
                print("You are unauthorized, please log in to use Cinemate")
                #await bot.send_message(user_id, "You are unauthorized, please log in to use Cinemate. /login")
                return None
    prepared_request = request.prepare()
    response = requests.Session().send(prepared_request)
    if response.status_code == 401:
        access_token = json.loads(response.request.body)["accessToken"]
        user_id = await db.get_user_by_access_token(access_token=access_token)
        await user_unauthorized(user_id)
    return response


# region Auth

async def sign_in_otp(email: str) -> requests.Response:
    url = f"{api_base_url}/auth/sign-in-otp"
    data = {"email": email}
    headers = {'Content-Type': 'application/json'}

    sign_in_otp_request = requests.Request(
        'POST',
        url=url,
        json=data,
        headers=headers
    )
    response = await send_request(sign_in_otp_request)
    return response


async def verify_otp(email, otp: str):
    url = f"{api_base_url}/auth/verify-otp"
    data = {"email": email,
            "token": otp}
    headers = {'Content-Type': 'application/json'}

    sign_in_otp_request = requests.Request(
        'POST',
        url=url,
        json=data,
        headers=headers
    )
    response = await send_request(sign_in_otp_request)
    return response


async def sign_out(user_id):
    url = f"{api_base_url}/auth/sign-out"

    access_token = await db.get_access_token(user_id)
    if access_token is None or access_token == "":
        await user_unauthorized(user_id)
        return None

    data = {"accessToken": access_token}

    headers = {'Content-Type': 'application/json'}

    set_favorite_movie_from_list_request = requests.Request(
        'POST',
        url=url,
        json=data,
        headers=headers
    )
    response = await send_request(set_favorite_movie_from_list_request)
    return response


# endregion

async def get_movie_list(user_id, is_favorite: int = None, score: int = None):
    url = f"{api_base_url}/movie-list/get-list"
    access_token = await db.get_access_token(user_id)
    if access_token is None or access_token == "":
        await user_unauthorized(user_id)
        return None

    data = {"accessToken": access_token}

    if is_favorite == '1':
        data["isFavorite"] = '1'

    if score is not None:
        data["score"] = score

    headers = {'Content-Type': 'application/json'}

    get_movie_list_request = requests.Request(
        'POST',
        url=url,
        json=data,
        headers=headers
    )
    response = await send_request(get_movie_list_request)
    return response


async def add_movie_to_list(user_id, movie_id):
    url = f"{api_base_url}/movie-list/add"
    access_token = await db.get_access_token(user_id)
    if access_token is None or access_token == "":
        await user_unauthorized(user_id)
        return None

    data = {"accessToken": access_token,
            "movieId": movie_id}

    headers = {'Content-Type': 'application/json'}

    add_movie_to_list_request = requests.Request(
        'POST',
        url=url,
        json=data,
        headers=headers
    )
    response = await send_request(add_movie_to_list_request)
    return response


async def remove_movie_to_list(user_id, movie_id):
    url = f"{api_base_url}/movie-list/remove"
    access_token = await db.get_access_token(user_id)
    if access_token is None or access_token == "":
        await user_unauthorized(user_id)
        return None

    data = {"accessToken": access_token,
            "movieId": movie_id}

    headers = {'Content-Type': 'application/json'}

    remove_movie_to_list_request = requests.Request(
        'POST',
        url=url,
        json=data,
        headers=headers
    )
    response = await send_request(remove_movie_to_list_request)
    return response


async def rate_movie_from_list(user_id, movie_id, score):
    url = f"{api_base_url}/movie-list/rate"

    access_token = await db.get_access_token(user_id)
    if access_token is None or access_token == "":
        await user_unauthorized(user_id)
        return None

    data = {"accessToken": access_token,
            "movieId": movie_id,
            "score": score}

    headers = {'Content-Type': 'application/json'}

    rate_movie_from_list_request = requests.Request(
        'POST',
        url=url,
        json=data,
        headers=headers
    )
    response = await send_request(rate_movie_from_list_request)
    return response


async def set_favorite_movie_from_list(user_id, movie_id, is_favorite: int):
    url = f"{api_base_url}/movie-list/set-favorite"

    access_token = await db.get_access_token(user_id)
    if access_token is None or access_token == "":
        await user_unauthorized(user_id)
        return None

    data = {"accessToken": access_token,
            "movieId": movie_id,
            "isFavorite": is_favorite}

    headers = {'Content-Type': 'application/json'}

    set_favorite_movie_from_list_request = requests.Request(
        'POST',
        url=url,
        json=data,
        headers=headers
    )
    response = await send_request(set_favorite_movie_from_list_request)
    return response


async def get_movies_by_title(title: str, page: int):
    url = f"{api_base_url}/movies"

    params = {"search-by": "title",
              "search-title": title,
              "page": page}

    headers = {'Content-Type': 'application/json'}

    get_movies_by_title_request = requests.Request(
        'GET',
        url=url,
        params=params,
        headers=headers
    )
    response = await send_request(get_movies_by_title_request)
    return response


async def get_movies_by_filters(page: int, year=None, country=None, genres=[]):
    url = f"{api_base_url}/movies"

    genres_str = ','.join(str(genre) for genre in genres)

    params = {"search-by": "filters",
              "page": page,
              "year": year,
              "country": country,
              "with-genres": genres_str
              }

    headers = {'Content-Type': 'application/json'}

    get_movies_by_filters_request = requests.Request(
        'GET',
        url=url,
        params=params,
        headers=headers
    )
    response = await send_request(get_movies_by_filters_request)
    print(response.url)
    return response


async def get_movie_by_id(movie_id: str):
    url = f"{api_base_url}/movies/{movie_id}"

    get_movies_by_id_request = requests.Request(
        'GET',
        url=url
    )
    response = await send_request(get_movies_by_id_request)
    return response


async def get_genres():
    url = f"{api_base_url}/genres"

    get_genres_request = requests.Request(
        'GET',
        url=url
    )
    response = await send_request(get_genres_request)
    return response


async def get_genres_by_id(genres_id: str):
    url = f"{api_base_url}/genres/{genres_id}"

    get_genres_by_id_request = requests.Request(
        'GET',
        url=url
    )
    response = await send_request(get_genres_by_id_request)
    return response


async def user_unauthorized(user_id):
    await bot.send_message(user_id, "You are unauthorized, please log in to use Cinemate. /login")
