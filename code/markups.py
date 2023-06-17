from telegram import ReplyKeyboardMarkup

MARKUPS = {
    "start": ReplyKeyboardMarkup(
        [["/weather", "/joke"]], one_time_keyboard=False, resize_keyboard=True
    ),
    "weather": ReplyKeyboardMarkup(
        [["/now", "/today"], ["/4days", "/back"]],
        one_time_keyboard=False,
        resize_keyboard=True,
    ),
}
