import json
import telebot
import bot_request
from bot_methods import add_button


city_request = dict()
hotels_request = []


def start_search(message, bot, sort_price):
    city_request['sort_price'] = sort_price
    hotels_request.clear()
    msg = bot.send_message(message.from_user.id, text='Напиши город, в котором ты хочешь найти отель')
    bot.register_next_step_handler(msg, get_city, bot)


def get_city(message, bot):
    try:
        city_request['city'] = message.text
        loading = bot.send_message(message.from_user.id, text='Пожалуйста, подождите...')
        response = bot_request.city_request(city_request['city'])
        city = json.loads(response.text)

        if city['suggestions'][0]['entities']:
            for i_entities in city['suggestions'][0]['entities']:
                if i_entities['name'].lower() == message.text.lower():
                    city_request['destinationId'] = i_entities['destinationId']
                    break
            else:
                raise Exception
        else:
            raise Exception

        bot.delete_message(message.chat.id, loading.message_id)
        msg = bot.send_message(message.from_user.id, text='Напиши количество отелей (не больше 10)')
        bot.register_next_step_handler(msg, get_number_hotels, bot)

    except Exception:
        bot.delete_message(message.chat.id, loading.message_id)
        msg = bot.send_message(message.from_user.id,
                               text='Неправильно введен город или такой город не найден. Попробуйте еще раз.')
        bot.register_next_step_handler(msg, get_city, bot)
        return


def get_number_hotels(message, bot):
    try:
        city_request['number_hotels'] = int(message.text)
        if city_request['number_hotels'] > 10:
            raise ValueError

        loading = bot.send_message(message.from_user.id, text='Пожалуйста, подождите...')
        response = bot_request.hotels_request(city_request, city_request['sort_price'])
        hotels = json.loads(response.text)
        bot.delete_message(message.chat.id, loading.message_id)

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

        if city_request['sort_price'] == 'PRICE':
            sorted(hotels_request, key=lambda hotel: hotel['price'])
        else:
            sorted(hotels_request, key=lambda hotel: hotel['price'], reverse=True)

        add_button(message, bot)

    except ValueError:
        msg = bot.send_message(message.from_user.id, text='Ошибка. Введите число от 1 до 10.')
        bot.register_next_step_handler(msg, get_number_hotels, bot)
        return
    except KeyError:
        bot.send_message(message.from_user.id, text='Ошибка запроса.')


def result(message, bot):
    city_request['photo_hotels'] = None
    for i_hotel in hotels_request:
        bot.send_message(message.from_user.id,
                         text=f'<b>"{i_hotel["name"]}"</b>\n '
                              f'Расстояние до цента: {i_hotel["distance to center"]}\n '
                              f'Цена: {i_hotel["price"]}\n '
                              f'Адрес: {i_hotel["address"]}\n '
                              f'Сайт: <a href="hotels.com/ho{i_hotel["id"]}">hotels.com/ho{i_hotel["id"]}</a>',
                         disable_web_page_preview=True
                         )


def get_photo_hotels(message, bot):
    try:
        city_request['photo_hotels'] = int(message.text)
        if city_request['photo_hotels'] > 10:
            raise ValueError

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
            response = bot_request.photo_request(i_hotel)
            photo_hotel = json.loads(response.text)

            for i_photo in photo_hotel['hotelImages']:
                if photo_count < city_request['photo_hotels']:
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
        bot.register_next_step_handler(msg, get_photo_hotels, bot)
        return
