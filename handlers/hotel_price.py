import json
import re
import telebot
from config_data import config
from users.user_info import Users
from loader import bot
from utils.bot_methods import add_button, add_calendar, add_history
from utils.bot_request import api_request


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
    try:
        user.city = message.text

        url = "https://hotels4.p.rapidapi.com/locations/v2/search"
        querystring = {
            "query": user.city,
            "locale": config.LOCALE,
            "currency": config.CURRENCY
        }
        city = api_request(url, querystring, message)

        if city['suggestions'][0]['entities']:
            for i_entities in city['suggestions'][0]['entities']:
                if i_entities['name'].lower() == message.text.lower():
                    user.city_id = i_entities['destinationId']
                    break
            else:
                raise ValueError
        else:
            raise KeyError

        bot.delete_message(message.chat.id, loading.message_id)
        bot.send_message(
            message.from_user.id,
            text='Выберите дату заезда.',
            reply_markup=add_calendar(message)
        )
        user.action = 'check_in'

    except (ValueError, KeyError, TypeError):
        bot.delete_message(message.chat.id, loading.message_id)
        msg = bot.send_message(
            message.from_user.id,
            text='Неправильно введен город или такой город не найден. '
                 'Попробуйте еще раз.'
        )
        bot.register_next_step_handler(msg, get_city)
        return


def get_number_hotels(message):
    loading = bot.send_message(
        message.from_user.id,
        text='Пожалуйста, подождите...'
    )
    user = Users.get_user(message.from_user.id)
    days = (user.check_out - user.check_in).days
    try:
        user.hotels_count = int(message.text)
        if user.hotels_count > 10:
            raise ValueError

        if user.command == '/highprice':
            sort_order = 'PRICE_HIGHEST_FIRST'
        elif user.command == '/beastdeal':
            sort_order = 'DISTANCE_FROM_LANDMARK'
        else:
            sort_order = 'PRICE'

        url = "https://hotels4.p.rapidapi.com/properties/list"
        querystring = {
            "destinationId": user.city_id,
            "pageNumber": 1,
            "pageSize": 25,
            "checkIn": user.check_in.strftime('%Y-%m-%d'),
            "checkOut": user.check_out.strftime('%Y-%m-%d'),
            "adults1": 1,
            "priceMin": user.min_price,
            "priceMax": user.max_price,
            "sortOrder": sort_order,
            "locale": config.LOCALE,
            "currency": config.CURRENCY,
            "landmarkIds": "Центр города"
        }
        hotels = api_request(url, querystring, message)
        with open('hotels.json', 'w', encoding='utf-8') as file:
            json.dump(hotels, file, indent=4, ensure_ascii=False)

        for i_hotel in hotels['data']['body']['searchResults']['results']:
            if len(user.hotel_list) < user.hotels_count:
                hotel_info = dict()
                hotel_info['id'] = i_hotel['id']
                hotel_info['name'] = i_hotel['name']
                hotel_info['address'] = \
                    f'{i_hotel["address"].get("locality", "")},' \
                    f'{i_hotel["address"].get("streetAddress", "")}, '\
                    f'{i_hotel["address"].get("postalCode", "")}, '\
                    f'{i_hotel["address"].get("extendedAddress", "")}'
                hotel_info['price'] = \
                    i_hotel['ratePlan']['price']['exactCurrent']
                hotel_info['total price'] = \
                    i_hotel['ratePlan']['price']['exactCurrent'] * days
                hotel_info['distance to center'] = \
                    ''.join(i_distance['distance']
                            for i_distance in i_hotel['landmarks']
                            if i_distance['label'] == 'Центр города')
            else:
                break

            if user.command == '/beastdeal':
                if user.min_distance < \
                        float(
                            re.search(
                                r'-?\d+,*\d*',
                                hotel_info['distance to center']
                            ).group().replace(',', '.')) \
                        < user.max_distance:
                    user.hotel_list.append(hotel_info)
            else:
                user.hotel_list.append(hotel_info)

        if user.command == '/lowprice':
            sorted(user.hotel_list,
                   key=lambda hotel: hotel['price']
                   )
        else:
            sorted(user.hotel_list,
                   key=lambda hotel: hotel['price'],
                   reverse=True
                   )

        bot.delete_message(message.chat.id, loading.message_id)
        add_history(message)
        add_button(message)

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
        url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

        bot.send_message(
            message.from_user.id,
            text=f'Найдено {len(user.hotel_list)} отелей:'
        )
        for i_hotel in user.hotel_list:
            photo = list()
            loading = bot.send_message(
                message.from_user.id,
                text='Пожалуйста, подождите...'
            )
            text = f'<b>"{i_hotel["name"]}"</b>\n' \
                   f'Расстояние до цента: {i_hotel["distance to center"]}\n' \
                   f'Цена за сутки: {i_hotel["price"]:,.2f} ' \
                   f'{config.CURRENCY}\n' \
                   f'Общая стоимость: {i_hotel["total price"]:,.2f}' \
                   f'{config.CURRENCY}\n' \
                   f'Адрес: {i_hotel["address"]}\n' \
                   f'Сайт: <a href="hotels.com/ho{i_hotel["id"]}">' \
                   f'hotels.com/ho{i_hotel["id"]}</a>'
            querystring = {"id": i_hotel['id']}
            photo_hotel = api_request(url, querystring, message)

            for i_photo in photo_hotel['hotelImages']:
                if len(photo) < user.photo_hotels:
                    photo.append(i_photo['baseUrl'].format(size='z'))
                else:
                    break

            bot.send_media_group(
                message.chat.id,
                media=[
                    telebot.types.InputMediaPhoto(
                        url_photo,
                        caption=text,
                        parse_mode='HTML'
                    )
                    if photo.index(url_photo) == 0
                    else telebot.types.InputMediaPhoto(url_photo)
                    for url_photo in photo]
            )
            bot.delete_message(message.chat.id, loading.message_id)

    except ValueError:
        msg = bot.send_message(
            message.from_user.id,
            text='Ошибка. Введите число от 1 до 10.'
        )
        bot.register_next_step_handler(msg, get_photo_hotels)
        return


def result(message):
    user = Users.get_user(message.from_user.id)
    bot.send_message(
        message.from_user.id,
        text=f'Найдено {len(user.hotel_list)} отелей:'
    )
    for i_hotel in user.hotel_list:
        bot.send_message(
            message.from_user.id,
            text=f'<b>"{i_hotel["name"]}"</b>\n '
                 f'Расстояние до цента: {i_hotel["distance to center"]}\n '
                 f'Цена за сутки: '
                 f'{i_hotel["price"]:,.2f} {config.CURRENCY}\n '
                 f'Общая стоимость: '
                 f'{i_hotel["total price"]:,.2f} {config.CURRENCY}\n '
                 f'Адрес: {i_hotel["address"]}\n '
                 f'Сайт: <a href="hotels.com/ho{i_hotel["id"]}">'
                 f'hotels.com/ho{i_hotel["id"]}</a>',
            disable_web_page_preview=True
        )


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
