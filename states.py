from aiogram.filters.state import State, StatesGroup


# states for register_next_step_handler for recommendations
class Recommendation(StatesGroup):
    message_request = State()
