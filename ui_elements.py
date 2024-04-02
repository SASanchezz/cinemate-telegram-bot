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
