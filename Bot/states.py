from aiogram.filters.state import State, StatesGroup


# states for register_next_step_handler for recommendations
class Recommendation(StatesGroup):
    similarity_request = State()
    expectation_request = State()


class Authorize(StatesGroup):
    wait_email = State()
    wait_otp = State()
