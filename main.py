import datetime
import telebot
from telebot import types
from config_data.config import DEFAULT_COMMANDS
from loader import bot, calendar, calendar_1_callback
from users.user_info import Users
from telebot.types import Message, CallbackQuery
from handlers.hotel_price import get_photo_hotels, min_price, get_number_hotels
from handlers.hotel_price import start_search, result
from handlers.history import history_command
from utils.bot_methods import add_calendar


@bot.message_handler(commands=['start'])
def start_command(message: Message) -> None:
    """
    Функция, которая запускает бота
    и начинает диалог с пользователем.

    :param message: передается сообщение чата телеграмм-бота.
    """
    bot.send_message(
        chat_id=message.from_user.id,
        text='Здравствуйте, {name}.\n'
             'Я помогу тебе подобрать отель.\n'
             'Для начала работы набери /help.'.
        format(name=message.from_user.first_name)
    )


@bot.message_handler(
    commands=['lowprice', 'beastdeal', 'history']
)
def price_command(message: Message) -> None:
    """
    Функция, обрабатывает команды и начинает
    поиск отелей или выводит историю поиска.

    :param message: передается сообщение чата телеграмм-бота.
    """
    user = Users.get_user(message.from_user.id)
    user.cleaning()
    user.command = message.text
    if message.text == '/history':
        history_command(message)
    else:
        start_search(message)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(calendar_1_callback.prefix)
)
def callback_inline(call: CallbackQuery) -> None:
    """
    Функция обрабатывает нажатие кнопки в календаре,
    записывает полученную дату и регистрирует следующий шаг поиска.

    :param call:
    """
    name, action, year, month, day = call.data.split(calendar_1_callback.sep)
    date = calendar.calendar_query_handler(
        bot=bot,
        call=call,
        name=name,
        action=action,
        year=year,
        month=month,
        day=day
    )
    user = Users.get_user(call.from_user.id)
    if action == 'DAY':
        if date < datetime.datetime.now():
            bot.send_message(
                chat_id=call.from_user.id,
                text='Ошибка. Дата не может быть меньше сегодняшней.\n '
                     'Выберите дату заезда.',
                reply_markup=add_calendar(call.message)
            )
            return
        elif user.check_in and date <= user.check_in:
            bot.send_message(
                chat_id=call.from_user.id,
                text='Ошибка. Дата не может быть меньше даты заезда.\n '
                     'Выберите дату выезда".',
                reply_markup=add_calendar(call.message)
            )
            return
        else:
            bot.send_message(
                chat_id=call.from_user.id,
                text=f"Вы выбрали: {date.strftime('%d.%m.%Y')}",
                reply_markup=types.ReplyKeyboardRemove()
            )
            if user.action == 'check_in':
                user.check_in = date
                bot.send_message(
                    chat_id=call.from_user.id,
                    text='Выберите дату выезда.',
                    reply_markup=add_calendar(call.message)
                )
                user.action = 'check_out'
            else:
                user.check_out = date

                if user.command == '/beastdeal':
                    msg = bot.send_message(
                        chat_id=call.from_user.id,
                        text='Напиши минимальную цену'
                    )
                    bot.register_next_step_handler(msg, min_price)
                else:
                    msg = bot.send_message(
                        chat_id=call.from_user.id,
                        text='Напиши количество отелей (не больше 10)'
                    )
                    bot.register_next_step_handler(msg, get_number_hotels)

    elif action == 'CANCEL':
        bot.send_message(
            chat_id=call.from_user.id,
            text='Отмена',
            reply_markup=types.ReplyKeyboardRemove()
        )


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call: CallbackQuery) -> None:
    """
    Функция обрабатывает нажатие на кнопку выбора фото отелей
    и регистрирует следующий шаг поиска.

    :param call:
    """
    if call.data == 'yes':
        msg = bot.send_message(
            chat_id=call.message.chat.id,
            text='Сколько фото показать? (не больше 10)'
        )
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(msg, get_photo_hotels)
    if call.data == 'no':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        result(call)


@bot.message_handler(commands=['help'])
def bot_help(message: Message) -> None:
    """
    Функция обрабатывает команду 'help' и выводит помощь в чат.

    :param message: передается сообщение чата телеграмм-бота.
    """
    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]
    bot.reply_to(message, '\n'.join(text))


@bot.message_handler(content_types=['text'])
def get_text_messages(message: Message) -> None:
    """
    Функция обрабатывает приветствие и неизвестные для бота команды.

    :param message: передается сообщение чата телеграмм-бота.
    """
    if message.text.lower() == 'привет':
        bot.send_message(
            chat_id=message.from_user.id,
            text='Привет, чем я могу тебе помочь?'
        )
    else:
        bot.send_message(
            chat_id=message.from_user.id,
            text='Я тебя не понимаю. Введите /help. '
        )


if __name__ == '__main__':
    bot.set_my_commands(
        [telebot.types.BotCommand(*i) for i in DEFAULT_COMMANDS]
    )
    bot.polling(none_stop=True)
