import telebot
from users.user_info import Users
from loader import bot
from telebot.types import Message
from utils.bot_methods import add_button, add_calendar, \
    add_history, declination, error_message
from utils.bot_request import city_request, hotel_request, hotel_details


def start_search(message: Message):
    """
    Функция начинает поиск и запрашивает у пользователя город поиска отелей.

    :param message: передается сообщение чата телеграмм-бота.
    """
    msg = bot.send_message(
        chat_id=message.from_user.id,
        text='Напиши город, в котором ты хочешь найти отель'
    )
    bot.register_next_step_handler(msg, get_city)


def get_city(message: Message):
    """
    Функция записывает город поиска и запрашивает дату заезда.

    :param message: передается сообщение чата телеграмм-бота.
    """
    loading = bot.send_message(
        chat_id=message.from_user.id,
        text='Пожалуйста, подождите...'
    )
    user = Users.get_user(message.from_user.id)
    user.city = message.text

    city_request(user, message)
    if not user.city_id:
        msg = bot.send_message(
            chat_id=message.from_user.id,
            text='Город не найден. '
                 'Попробуйте еще раз.'
        )
        bot.register_next_step_handler(msg, get_city)
        return

    bot.delete_message(message.chat.id, loading.message_id)
    bot.send_message(
        chat_id=message.from_user.id,
        text='Выберите дату заезда.',
        reply_markup=add_calendar(message)
    )
    user.action = 'check_in'


def get_number_hotels(message: Message):
    """
    Функция записывает количество отелей для поиска
    и выводит кнопки выбора фото.

    :param message: передается сообщение чата телеграмм-бота.
    """
    loading = bot.send_message(
        chat_id=message.from_user.id,
        text='Пожалуйста, подождите...'
    )
    user = Users.get_user(message.from_user.id)
    try:
        user.hotels_count = int(message.text)
        if user.hotels_count > 10:
            raise ValueError

        add_button(message)
        bot.delete_message(message.chat.id, loading.message_id)

    except ValueError:
        msg = bot.send_message(
            chat_id=message.from_user.id,
            text='Ошибка. Введите число от 1 до 10.'
        )
        bot.register_next_step_handler(msg, get_number_hotels)
        return


def get_photo_hotels(message: Message):
    """
    Функция записывает количество фото для отеля, выводит краткую
    инфу о отеле в чат и записывает команду в историю.

    :param message: передается сообщение чата телеграмм-бота.
    """
    user = Users.get_user(message.from_user.id)
    try:

        user.photo_hotels = int(message.text)
        if user.photo_hotels > 10:
            raise ValueError

        loading = bot.send_message(
            chat_id=message.from_user.id,
            text='Пожалуйста, подождите...'
        )
        hotel_request(user, message)
        bot.delete_message(message.chat.id, loading.message_id)

        amount_hotels = len(user.hotel_list)
        bot.send_message(
            chat_id=message.from_user.id,
            text=f'Найдено {amount_hotels} '
                 f'отел{declination(amount_hotels, "hotel")}:'
        )
        amount_days = (user.check_out - user.check_in).days
        hotel_count = 1
        for i_hotel in user.hotel_list:
            info = hotel_details(user, i_hotel["id"], message)
            text = f'<b>{hotel_count} "{i_hotel["name"]}"</b>\n'\
                   f'Расстояние до цента: ' \
                   f'{i_hotel["distance to center"]} Км\n'\
                   f'Цена за сутки: {i_hotel["price"]:,.2f}$\n' \
                   f'Цена за {amount_days} {declination(amount_days, "day")}:'\
                   f' {i_hotel["total price"]:,.2f}$\n'\
                   f'Адрес: {info[0]}\n'\
                   f'Сайт: '\
                   f'<a href="www.hotels.com/' \
                   f'h{i_hotel["id"]}.Hotel-Information">'\
                   f'hotels.com/h{i_hotel["id"]}</a>'

            bot.send_media_group(
                chat_id=message.chat.id,
                media=[
                    telebot.types.InputMediaPhoto(
                        url_photo,
                        caption=text,
                        parse_mode='HTML'
                    )
                    if info[1].index(url_photo) == 0
                    else telebot.types.InputMediaPhoto(url_photo)
                    for url_photo in info[1]]
            )
            hotel_count += 1

        add_history(message)

    except ValueError:
        msg = bot.send_message(
            chat_id=message.from_user.id,
            text='Ошибка. Введите число от 1 до 10.'
        )
        bot.register_next_step_handler(msg, get_photo_hotels)
        return
    except Exception:
        error_message(message)


def result(message):
    """
    Функция выводит результат поиска отелей без фото в чат
    и записывает команду в историю поиска.

    :param message: передается сообщение чата телеграмм-бота.
    """
    user = Users.get_user(message.from_user.id)
    loading = bot.send_message(
        chat_id=message.from_user.id,
        text='Пожалуйста, подождите...'
    )
    hotel_request(user, message)
    amount_hotels = len(user.hotel_list)
    bot.delete_message(message.message.chat.id, loading.message_id)
    bot.send_message(
        chat_id=message.from_user.id,
        text=f'Найдено {amount_hotels} '
             f'отел{declination(amount_hotels, "hotel")}:'
    )
    amount_days = (user.check_out - user.check_in).days
    hotel_count = 1
    for i_hotel in user.hotel_list:
        new_loading = bot.send_message(
            chat_id=message.from_user.id,
            text='Пожалуйста, подождите...'
        )
        info = hotel_details(user, i_hotel["id"], message)

        bot.send_message(
            chat_id=message.from_user.id,
            text=f'<b>{hotel_count} "{i_hotel["name"]}"</b>\n '
                 f'Расстояние до цента: {i_hotel["distance to center"]} Км\n '
                 f'Цена за сутки: '
                 f'{i_hotel["price"]:,.2f}$\n '
                 f'Цена за {amount_days} {declination(amount_days, "day")}: '
                 f'{i_hotel["total price"]:,.2f}$\n '
                 f'Адрес: {info[0]}\n '
                 f'Сайт: '
                 f'<a href="hotels.com/h{i_hotel["id"]}.Hotel-Information">'
                 f'hotels.com/h{i_hotel["id"]}</a>',
            disable_web_page_preview=True
        )
        bot.delete_message(message.message.chat.id, new_loading.message_id)
        hotel_count += 1

    add_history(message)


def min_price(message: Message):
    """
    Функция записывает минимальную цену отеля.

    :param message: передается сообщение чата телеграмм-бота.
    """
    try:
        user = Users.get_user(message.from_user.id)
        user.min_price = int(message.text)
        msg = bot.send_message(
            chat_id=message.from_user.id,
            text='Напиши максимальную цену.'
        )
        bot.register_next_step_handler(msg, max_price)
    except ValueError:
        msg = bot.send_message(
            chat_id=message.from_user.id,
            text='Ошибка. Цена может содержать только целое число.'
        )
        bot.register_next_step_handler(msg, min_price)
        return


def max_price(message: Message):
    """
    Функция записывает максимальную цену отеля.

    :param message: передается сообщение чата телеграмм-бота.
    """
    try:
        user = Users.get_user(message.from_user.id)
        user.max_price = int(message.text)
        msg = bot.send_message(
            chat_id=message.from_user.id,
            text='Напиши количество отелей (не больше 10)'
        )
        bot.register_next_step_handler(msg, get_number_hotels)

    except ValueError:
        msg = bot.send_message(
            chat_id=message.from_user.id,
            text='Ошибка. Цена может содержать только целое число.'
        )
        bot.register_next_step_handler(msg, max_price)
        return

