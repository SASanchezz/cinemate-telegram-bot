import g4f


async def recommendation_generator(recommendation_type, params):
    """
    Function to get recommendations due to the given film name using YOU.COM AI
    :param recommendation_type: str - type of recommendations (similarity or expectation)
    :param params: str - name of film or film expectation
    :return: str - recommendations
    """
    try:
        provider = g4f.Provider.You
        res = ""
        if recommendation_type == 'similarity':
            content = f"Generate me a list of films similar to {params}"
        else:
            content = f"Generate me a list of films which will satisfy these expectations: {params}"
        response_chat = await g4f.ChatCompletion.create_async(
            model=g4f.models.default,
            messages=[{"role": "user", "content": content}],
            provider=provider
        )
        for message in response_chat:
            res += message
        return res
    except Exception as e:
        print(f"Error occurred {e}")
        return "Something went wrong\n._. Try again ._."
