import telebot
from config_data import config
from users.user_info import Users
from loader import bot
from utils.bot_methods import add_button, add_calendar, add_history, declination
from utils.bot_request import city_request, hotel_request


def start_search(message):
    msg = bot.send_message(
        message.from_user.id,
        text='Напиши город, в котором ты хочешь найти отель'
    )
    bot.register_next_step_handler(msg, get_city)


def get_city(message):
    loading = bot.send_message(
        message.from_user.id,
        text='Пожалуйста, подождите...'
    )
    user = Users.get_user(message.from_user.id)
    user.city = message.text

    city_request(user, message)
    if not user.city_id:
        msg = bot.send_message(
            message.from_user.id,
            text='Город не найден.'
                 'Попробуйте еще раз.'
        )
        bot.register_next_step_handler(msg, get_city)
        return

    bot.delete_message(message.chat.id, loading.message_id)
    bot.send_message(
        message.from_user.id,
        text='Выберите дату заезда.',
        reply_markup=add_calendar(message)
    )
    user.action = 'check_in'


def get_number_hotels(message):
    loading = bot.send_message(
        message.from_user.id,
        text='Пожалуйста, подождите...'
    )
    user = Users.get_user(message.from_user.id)
    try:
        user.hotels_count = int(message.text)
        if user.hotels_count > 10:
            raise ValueError

        add_button(message)
        bot.delete_message(message.chat.id, loading.message_id)

    except (ValueError, KeyError):
        msg = bot.send_message(
            message.from_user.id,
            text='Ошибка. Введите число от 1 до 10.'
        )
        bot.register_next_step_handler(msg, get_number_hotels)
        return


def get_photo_hotels(message):
    user = Users.get_user(message.from_user.id)
    try:

        user.photo_hotels = int(message.text)
        if user.photo_hotels > 10:
            raise ValueError

    except ValueError:
        msg = bot.send_message(
            message.from_user.id,
            text='Ошибка. Введите число от 1 до 10.'
        )
        bot.register_next_step_handler(msg, get_photo_hotels)
        return
    loading = bot.send_message(
        message.from_user.id,
        text='Пожалуйста, подождите...'
    )
    hotel_request(user, message)
    add_history(message)
    bot.delete_message(message.chat.id, loading.message_id)
    amount_hotels = len(user.hotel_list)
    bot.send_message(
        message.from_user.id,
        text=f'Найдено {amount_hotels} отел{declination(amount_hotels)}:'
    )
    amount_days = (user.check_out - user.check_in).days
    for i_hotel in user.hotel_list:
        text = f'<b>"{i_hotel["name"]}"</b>\n' \
               f'Расстояние до цента: {i_hotel["distance to center"]} Км\n' \
               f'Цена за сутки: {i_hotel["price"]:,.2f}$\n' \
               f'Цена за {amount_days} дн{declination(amount_days)}: ' \
               f'{i_hotel["total price"]:,.2f}$\n' \
               f'Адрес: {i_hotel["address"]}\n' \
               f'Сайт: ' \
               f'<a href="www.hotels.com/h{i_hotel["id"]}.Hotel-Information">'\
               f'hotels.com/h{i_hotel["id"]}</a>'

        bot.send_media_group(
            message.chat.id,
            media=[
                telebot.types.InputMediaPhoto(
                    url_photo,
                    caption=text,
                    parse_mode='HTML'
                )
                if i_hotel['photo'].index(url_photo) == 0
                else telebot.types.InputMediaPhoto(url_photo)
                for url_photo in i_hotel['photo']]
        )


def result(message):
    user = Users.get_user(message.from_user.id)
    loading = bot.send_message(
        message.from_user.id,
        text='Пожалуйста, подождите...'
    )
    hotel_request(user, message)
    add_history(message)
    amount_hotels = len(user.hotel_list)
    bot.send_message(
        message.from_user.id,
        text=f'Найдено {amount_hotels} отел{declination(amount_hotels)}:'
    )
    amount_days = (user.check_out - user.check_in).days
    for i_hotel in user.hotel_list:
        bot.send_message(
            message.from_user.id,
            text=f'<b>"{i_hotel["name"]}"</b>\n '
                 f'Расстояние до цента: {i_hotel["distance to center"]} Км\n '
                 f'Цена за сутки: '
                 f'{i_hotel["price"]:,.2f}$\n '
                 f'Цена за {amount_days} дн{declination(amount_days)} '
                 f'{i_hotel["total price"]:,.2f}$\n '
                 f'Адрес: {i_hotel["address"]}\n '
                 f'Сайт: '
                 f'<a href="hotels.com/ho{i_hotel["id"]}.Hotel-Information">'
                 f'hotels.com/h{i_hotel["id"]}</a>',
            disable_web_page_preview=True
        )
    bot.delete_message(message.message.chat.id, loading.message_id)


def min_price(message):
    try:
        user = Users.get_user(message.from_user.id)
        user.min_price = int(message.text)

    except ValueError:
        msg = bot.send_message(
            message.from_user.id,
            text='Ошибка. Цена может содержать только цифры.'
        )
        bot.register_next_step_handler(msg, min_price)
        return

    msg = bot.send_message(
        message.from_user.id,
        text='Напиши максимальную цену.'
    )
    bot.register_next_step_handler(msg, max_price)


def max_price(message):
    try:
        user = Users.get_user(message.from_user.id)
        user.max_price = int(message.text)

    except ValueError:
        msg = bot.send_message(
            message.from_user.id,
            text='Ошибка. Цена может содержать только цифры.'
        )
        bot.register_next_step_handler(msg, max_price)
        return

    msg = bot.send_message(
        message.from_user.id,
        text='Напиши минимальное расстояние до центра.'
    )
    bot.register_next_step_handler(msg, min_distance)


def min_distance(message):
    try:
        user = Users.get_user(message.from_user.id)
        user.min_distance = int(message.text)

    except ValueError:
        msg = bot.send_message(
            message.from_user.id,
            text='Ошибка. Расстояние может содержать только цифры.'
        )
        bot.register_next_step_handler(msg, min_distance)
        return

    msg = bot.send_message(
        message.from_user.id,
        text='Напиши максимальное расстояние до центра.'
    )
    bot.register_next_step_handler(msg, max_distance)


def max_distance(message):
    try:
        user = Users.get_user(message.from_user.id)
        user.max_distance = int(message.text)

    except ValueError:
        msg = bot.send_message(
            message.from_user.id,
            text='Ошибка. Расстояние может содержать только цифры.'
        )
        bot.register_next_step_handler(msg, max_distance)
        return

    msg = bot.send_message(
        message.from_user.id,
        text='Напиши количество отелей (не больше 10)'
    )
    bot.register_next_step_handler(msg, get_number_hotels)
