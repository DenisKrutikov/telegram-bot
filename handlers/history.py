import sqlite3
from datetime import datetime
from loader import bot
from telebot.types import Message


def history_command(message: Message) -> None:
    """
    Функция, которая выводит в чат историю поиска пользователя.

    :param message: передается сообщение чата телеграмм-бота.
    """
    try:
        with sqlite3.connect('database/search_history.db') \
                as sqlite_connection:
            cursor = sqlite_connection.cursor()
            cursor.execute(
                'SELECT command, command_date, city, hotels '
                'FROM history '
                'WHERE user_id = ?',
                (message.from_user.id,)
            )
            total_rows = cursor.fetchall()

            if total_rows:
                bot.send_message(
                    chat_id=message.from_user.id,
                    text='История поиска отелей:'
                )

                for i_rows in total_rows:
                    date = datetime.strptime(
                        i_rows[1],
                        "%Y-%m-%d %H:%M:%S.%f"
                    )
                    text = f'<b>Команда:</b> {i_rows[0]}\n' \
                           f'<b>Дата команды:</b> ' \
                           f'{date.strftime("%d.%m.%Y %H:%M:%S")}\n' \
                           f'<b>Город:</b> {i_rows[2]}\n' \
                           f'<b>Список отелей:</b> {i_rows[3]}'
                    bot.send_message(
                        chat_id=message.from_user.id,
                        text=text,
                        disable_web_page_preview=True
                    )
            else:
                bot.send_message(
                    chat_id=message.from_user.id,
                    text='История поиска пуста'
                )

    except sqlite3.OperationalError:
        bot.send_message(
            chat_id=message.from_user.id,
            text='Ошибка сервиса. Попробуйте еще раз.'
        )
