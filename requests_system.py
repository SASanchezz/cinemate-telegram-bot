import requests

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
