from aiogram import types


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
