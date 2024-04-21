from aiogram import types
from Bot import requests_system

# start menu (ReplyKeyboardMarkup)
def get_start_menu():
    kb = [
        [
            types.KeyboardButton(text='Search by name'),
            types.KeyboardButton(text='Search by criteria')
        ],
        [
            types.KeyboardButton(text='Recommend me'),
            types.KeyboardButton(text='My movielist')
        ]
    ]

    return types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Choose what do you want to do'
    )


# recommendation main menu (InlineKeyboardMarkup)
def get_recommendation_main_menu():
    kb = [
        [
            types.InlineKeyboardButton(text='Due to my movielist', callback_data="recommendation_movielist"),
        ],
        [
            types.InlineKeyboardButton(text='Similar to', callback_data="recommendation_similarity"),
        ],
        [
            types.InlineKeyboardButton(text='Describe my expectation', callback_data="recommendation_expectation"),
        ],
        [
            types.InlineKeyboardButton(text='Back', callback_data="back_main"),
        ]
    ]

    return types.InlineKeyboardMarkup(
        inline_keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=True
    )


# recommendation additional menu (InlineKeyboardMarkup)
def get_recommendation_additional_menu(recommend_type):
    kb = [
        [
            types.InlineKeyboardButton(text='Try again', callback_data=f"recommendation_regenerate_{recommend_type}"),
        ],
        [
            types.InlineKeyboardButton(text='Back', callback_data="back_recommend"),
        ]
    ]

    return types.InlineKeyboardMarkup(
        inline_keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=True
    )

# MENU for movie information options
async def get_movie_by_name_info_keyboard(movie_id, user_id):
    response = await requests_system.get_movie_list(user_id=user_id)
    if response.status_code == 200:
        movie_list = response.json()
        movie_ids = [movie['id'] for movie in movie_list]
        is_in_movielist = int(movie_id) in movie_ids
    else:
        is_in_movielist = False
    movielist_button_text = "Delete from movielist" if is_in_movielist else "Add to movielist"

    kb = [
        [
            types.InlineKeyboardButton(text='Info', callback_data=f'info_{movie_id}'),
            types.InlineKeyboardButton(text='Overview', callback_data=f'overview_{movie_id}'),
            types.InlineKeyboardButton(text='Genres', callback_data=f'genres_{movie_id}'),
            types.InlineKeyboardButton(text='Rate', callback_data=f'rate_movie_{movie_id}'),
        ],
        [
            types.InlineKeyboardButton(text=movielist_button_text, callback_data=f'toggle_movielist_{movie_id}')
        ],
        [
            types.InlineKeyboardButton(text='Add to favourites', callback_data=f'add_to_favorite_{movie_id}')
        ],
        [
            types.InlineKeyboardButton(text='Back', callback_data='back_main')
        ]
    ]

    return types.InlineKeyboardMarkup(inline_keyboard=kb)

#MENU FOR CHOICE WITH PAGES
def get_movie_choice_menu(movie_results, current_page, total_pages):
    kb = []
    for movie in movie_results:
        movie_button = types.InlineKeyboardButton(
            text=f"{movie['title']} ({movie['release_date'][:4]})",
            callback_data=f"choose_movie_{movie['id']}"
        )
        kb.append([movie_button])

    pagination_buttons = []
    if total_pages > 1:
        if current_page > 1:
            pagination_buttons.append(types.InlineKeyboardButton(
                text="<< Prev",
                callback_data=f"prev_page_{current_page - 1}"
            ))
        if current_page < total_pages:
            pagination_buttons.append(types.InlineKeyboardButton(
                text="Next >>",
                callback_data=f"next_page_{current_page + 1}"
            ))
    kb.append(pagination_buttons)

    kb.append([types.InlineKeyboardButton(text="Back", callback_data="back_main")])
    return types.InlineKeyboardMarkup(inline_keyboard=kb)
