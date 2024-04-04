import requests
import db

# region Authentication

api_base_url = "https://cinemate.space/api/v1"


async def send_request(request: requests.Request) -> requests.Response:
    prepared_request = request.prepare()
    response = requests.Session().send(prepared_request)
    return response


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


# endregion
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


async def get_movie_list(user_id, is_favorite: int = None, score: int = None):
    url = f"{api_base_url}/movie-list/get-list"
    access_token = await db.get_access_token(user_id)
    if access_token is None:
        return

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
    if access_token is None:
        return

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
    if access_token is None:
        return

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
    if access_token is None:
        return

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
    if access_token is None:
        return

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
