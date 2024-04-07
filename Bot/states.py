from aiogram.filters.state import State, StatesGroup


# states for register_next_step_handler for recommendations
class Recommendation(StatesGroup):
    similarity_request = State()
    expectation_request = State()

class MovieSearch(StatesGroup):
    wait_movie_name = State()
    wait_rate = State()

class Authorize(StatesGroup):
    wait_email = State()
    wait_otp = State()

class FilterSteps(StatesGroup):
    handle_year = State()
    handle_genre = State()
    handle_country = State()
