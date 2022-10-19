import datetime
from loader import bot
from telebot import types
from utils.bot_calendar import Calendar, RUSSIAN_LANGUAGE, CallbackData


calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1_callback = CallbackData("calendar_1", "action", "year", "month", "day")


def add_button(message):
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Показать', callback_data='yes')
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text='Ненужно', callback_data='no')
    keyboard.add(key_no)
    bot.send_message(message.from_user.id, text='Показать фото отелей?', reply_markup=keyboard)


def add_calendar(message):
    now = datetime.datetime.now()
    bot.send_message(
        message.chat.id,
        f"Календарь:",
        reply_markup=calendar.create_calendar(
            name=calendar_1_callback.prefix,
            year=now.year,
            month=now.month,
        ),
    )


