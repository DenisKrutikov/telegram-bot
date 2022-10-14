import telebot
from config_data import config
from users.user_info import Users
from loader import bot
from utils.bot_methods import add_button, add_calendar
from utils.bot_request import api_request

hotels_request = []


def start_search(message):
    hotels_request.clear()
    msg = bot.send_message(message.from_user.id, text='Напиши город, в котором ты хочешь найти отель')
    bot.register_next_step_handler(msg, get_city)


def get_city(message):
    loading = bot.send_message(message.from_user.id, text='Пожалуйста, подождите...')
    try:
        user = Users.get_user(message.from_user.id)
        user.city = message.text

        url = "https://hotels4.p.rapidapi.com/locations/v2/search"
        querystring = {"query": user.city, "locale": config.LOCALE, "currency": config.CURRENCY}
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
            text='Неправильно введен город или такой город не найден. Попробуйте еще раз.'
        )
        bot.register_next_step_handler(msg, get_city)
        return


def get_number_hotels(message):
    loading = bot.send_message(message.from_user.id, text='Пожалуйста, подождите...')
    try:
        user = Users.get_user(message.from_user.id)
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
            "pageSize": user.hotels_count,
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

        for i_hotel in hotels['data']['body']['searchResults']['results']:
            hotels_request.append(
                {
                    'id': i_hotel['id'],
                    'name': i_hotel['name'],
                    'address': f'{i_hotel["address"].get("locality", "")}, '
                               f'{i_hotel["address"].get("streetAddress", "")}, '
                               f'{i_hotel["address"].get("postalCode", "")}, '
                               f'{i_hotel["address"].get("extendedAddress", "")}',
                    'price': i_hotel['ratePlan']['price']['current'],
                    'distance to center': ''.join(i_distance['distance']
                                                  for i_distance in i_hotel['landmarks']
                                                  if i_distance['label'] == 'Центр города')
                }
            )

        if user.command == '/lowprice':
            sorted(hotels_request, key=lambda hotel: hotel['price'])
        else:
            sorted(hotels_request, key=lambda hotel: hotel['price'], reverse=True)

        bot.delete_message(message.chat.id, loading.message_id)
        add_button(message)

    except ValueError:
        msg = bot.send_message(message.from_user.id, text='Ошибка. Введите число от 1 до 10.')
        bot.register_next_step_handler(msg, get_number_hotels)
        return
    except KeyError:
        bot.send_message(message.from_user.id, text='Ошибка запроса.')


def get_photo_hotels(message):
    try:
        user = Users.get_user(message.from_user.id)
        user.photo_hotels = int(message.text)
        if user.photo_hotels > 10:
            raise ValueError
        url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

        bot.send_message(message.from_user.id, text='Результат поиска:')

        for i_hotel in hotels_request:
            photo_count = 0
            photo = list()
            loading = bot.send_message(message.from_user.id, text='Пожалуйста, подождите...')
            text = f'<b>"{i_hotel["name"]}"</b>\n '\
                   f'Расстояние до цента: {i_hotel["distance to center"]}\n '\
                   f'Цена: {i_hotel["price"]}\n '\
                   f'Адрес: {i_hotel["address"]}\n '\
                   f'Сайт: <a href="hotels.com/ho{i_hotel["id"]}">hotels.com/ho{i_hotel["id"]}</a>'
            querystring = {"id": i_hotel['id']}
            photo_hotel = api_request(url, querystring, message)

            for i_photo in photo_hotel['hotelImages']:
                if photo_count < user.photo_hotels:
                    photo_count += 1
                    photo.append(i_photo['baseUrl'].format(size='z'))
                else:
                    break

            bot.delete_message(message.chat.id, loading.message_id)
            bot.send_media_group(message.chat.id,
                                 media=
                                 [
                                     telebot.types.InputMediaPhoto(url_photo, caption=text, parse_mode='HTML')
                                     if photo.index(url_photo) == 0
                                     else telebot.types.InputMediaPhoto(url_photo)
                                     for url_photo in photo
                                 ]
                                 )

    except ValueError:
        msg = bot.send_message(message.from_user.id, text='Ошибка. Введите число от 1 до 10.')
        bot.register_next_step_handler(msg, get_photo_hotels)
        return


def result(message):
    bot.send_message(message.from_user.id, text='Результат поиска:')
    for i_hotel in hotels_request:
        bot.send_message(message.from_user.id,
                         text=f'<b>"{i_hotel["name"]}"</b>\n '
                              f'Расстояние до цента: {i_hotel["distance to center"]}\n '
                              f'Цена: {i_hotel["price"]}\n '
                              f'Адрес: {i_hotel["address"]}\n '
                              f'Сайт: <a href="hotels.com/ho{i_hotel["id"]}">hotels.com/ho{i_hotel["id"]}</a>',
                         disable_web_page_preview=True
                         )
