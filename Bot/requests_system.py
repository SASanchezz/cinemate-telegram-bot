import requests

# region Authentication

api_base_url = "http://cinemate.space/api/v1"


async def sign_in(email: str):
    responce = requests.post(
        f"{api_base_url}/auth/sign-in",
        data={
            "email": f"{email}"
        }
    )
    print(responce)
    return responce
# endregion
