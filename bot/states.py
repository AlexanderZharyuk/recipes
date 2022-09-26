from enum import Enum, auto


class States(Enum):
    ACCEPT_PRIVACY = auto()
    START_REGISTRATION = auto()
    USER_FULLNAME = auto()
    USER_PHONE_NUMBER = auto()
    MAIN_MENU = auto()
    CATEGORY = auto()
    RECIPE = auto()
    USER_RECIPES = auto()
    FAVORITE_RECIPE = auto()
