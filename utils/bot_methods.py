import datetime
import sqlite3
from typing import List
from loader import bot, calendar, calendar_1_callback
from telebot import types
from users.user_info import Users
from telebot.types import Message


def add_button(message: Message) -> None:
    """
    Функция добавляет в чат телеграмма кнопки выбора фото.

    :param message: передается сообщение чата телеграмм-бота.
    """
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


def add_calendar(message: Message) -> None:
    """
    Функция, которая создает календарь за текущий месяц.

    :param message: передается сообщение чата телеграмм-бота.
    """
    now = datetime.datetime.now()
    bot.send_message(
        chat_id=message.chat.id,
        text='Календарь:',
        reply_markup=calendar.create_calendar(
            name=calendar_1_callback.prefix,
            year=now.year,
            month=now.month,
        ),
    )


def add_history(message: Message) -> None:
    """
    Функция, которая добавляет в базу данных запись о запросе пользователя.
    Включает: команду, дату команды, город и список отелей.

    :param message: передается сообщение чата телеграмм-бота.
    """
    try:
        user = Users.get_user(message.from_user.id)
        with sqlite3.connect('database/search_history.db') \
                as sqlite_connection:
            cursor = sqlite_connection.cursor()
            cursor.execute('INSERT INTO history VALUES (?, ?, ?, ?, ?)',
                           (message.from_user.id,
                            user.command,
                            datetime.datetime.now(),
                            user.city.capitalize(),
                            ', '.join(f'<a href="www.hotels.com/'
                                      f'h{i_hotel["id"]}.Hotel-Information">'
                                      f'{i_hotel["name"]}</a>'
                                      for i_hotel in user.hotel_list)
                            )
                           )
    except sqlite3.OperationalError:
        error_message(message)


def declination(number: int, option: str) -> str:
    """
    Функция, которая склоняет окончания слова день или отель.

    :param number: передается день месяца
    :param option: передается выбор склоняемого слова.
    :return: возвращает окончание слова, склоненное слово.
    """
    exclusion_list: List[int] = [11, 12, 13, 14]
    number = number % 10
    if option == 'hotel':
        if number == 1 and number not in exclusion_list:
            return 'ь'
        elif number in [2, 3, 4] and number not in exclusion_list:
            return 'я'
        else:
            return 'ей'
    elif option == 'day':
        if number == 1 and number not in exclusion_list:
            return 'день'
        elif number in [2, 3, 4] and number not in exclusion_list:
            return 'дня'
        else:
            return 'дней'


def error_message(message: Message) -> None:
    """
    Функция, которая выводит сообщение об ошибке в чат бота.

    :param message: передается сообщение чата телеграмм-бота.
    """
    bot.send_message(
        chat_id=message.from_user.id,
        text='Сервис временно не доступен.'
    )
