from aiogram.fsm.state import State, StatesGroup

class AuthForm(StatesGroup):
    base_message = State()
    last_message = State()
    site = State()
    login = State()
    password = State()

class InlineDownloadForm(StatesGroup):
    base_message = State()
    last_message = State()
    start_page = State()
    end_page = State()
    proxy = State()

class SetupSiteForm(StatesGroup):
    base_message = State()
    last_message = State()
    site = State()
    filename = State()
    proxy = State()

class SetupAccountForm(StatesGroup):
    base_message = State()
    filename = State()