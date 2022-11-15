import datetime
import sqlite3
from loader import bot
from telebot import types
from telebot_calendar import Calendar, RUSSIAN_LANGUAGE, CallbackData
from users.user_info import Users


calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1_callback = CallbackData(
    "calendar_1", "action", "year", "month", "day"
)


def add_button(message):
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(
        text='Показать',
        callback_data='yes'
    )
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(
        text='Ненужно',
        callback_data='no'
    )
    keyboard.add(key_no)
    bot.send_message(
        message.from_user.id,
        text='Показать фото отелей?',
        reply_markup=keyboard
    )


def add_calendar(message):
    now = datetime.datetime.now()
    bot.send_message(
        message.chat.id,
        text='Календарь:',
        reply_markup=calendar.create_calendar(
            name=calendar_1_callback.prefix,
            year=now.year,
            month=now.month,
        ),
    )


def add_history(message):
    user = Users.get_user(message.from_user.id)
    hotels = (i_hotel['name'] for i_hotel in user.hotel_list)
    with sqlite3.connect('database/search_history.db') as sqlite_connection:
        cursor = sqlite_connection.cursor()
        cursor.execute('INSERT INTO history VALUES (?, ?, ?, ?, ?)',
                       (message.from_user.id,
                        user.command,
                        datetime.datetime.now(),
                        user.city,
                        ', '.join(hotels))
                       )
