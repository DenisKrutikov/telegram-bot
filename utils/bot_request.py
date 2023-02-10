import json
import requests
from typing import Dict, Tuple
from config_data import config
from telebot.types import Message
from users.user_info import Users
from utils.bot_methods import error_message


def api_request(url: str,
                payload: dict,
                method_type: str,
                message: Message
                ) -> Dict:
    """
    Функция, которая делает запрос к API.

    :param url: передается ссылка на запрос.
    :param payload: передаются параметры запроса.
    :param method_type: передается тип метода запроса.
    :param message: передается сообщение чата телеграмм-бота.
    :return: возвращается словарь с данными.
    """
    try:
        timeout = 10
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": config.RAPID_API_KEY,
            "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
        }

        if method_type == 'GET':
            response = requests.get(
                url=url,
                headers=headers,
                params=payload,
                timeout=timeout
            )
        else:
            response = requests.post(
                url=url,
                json=payload,
                headers=headers,
                timeout=timeout
            )

        if response.status_code == requests.codes.ok:
            return json.loads(response.text)

    except Exception:
        error_message(message)


def city_request(user: Users, message: Message) -> None:
    """
    Функция, которая обрабатывает ответ запроса и получает id города.

    :param user: передается пользователь.
    :param message: передается сообщение чата телеграмм-бота.
    """
    try:
        url = 'https://hotels4.p.rapidapi.com/locations/v3/search'

        payload = {'q': user.city, 'locale': config.LOCALE}

        city = api_request(url, payload, 'GET', message)

        for i_city in city['sr']:
            city_name = i_city['regionNames']['shortName'].lower()
            if i_city['type'] == 'CITY' and city_name == user.city.lower():
                user.city_id = i_city['gaiaId']

    except Exception:
        error_message(message)


def hotel_request(user: Users, message: Message) -> None:
    """
    Функция, которая обрабатывает ответ запроса и получает данные по отелям.

    :param user: передается пользователь.
    :param message: передается сообщение чата телеграмм-бота.
    """
    try:
        if user.command == '/beastdeal':
            sort_order = 'DISTANCE'
        else:
            sort_order = 'PRICE_LOW_TO_HIGH'

        url = 'https://hotels4.p.rapidapi.com/properties/v2/list'

        payload = {
            'currency': config.CURRENCY,
            'eapid': 1,
            'locale': config.LOCALE,
            'destination': {'regionId': user.city_id},
            'checkInDate': {
                'day': user.check_in.day,
                'month': user.check_in.month,
                'year': user.check_in.year
            },
            'checkOutDate': {
                'day': user.check_out.day,
                'month': user.check_out.month,
                'year': user.check_out.year
            },
            'rooms': [
                {
                    'adults': 1,
                    'children': []
                }
            ],
            'resultsStartingIndex': 0,
            'resultsSize': user.hotels_count,
            'sort': sort_order,
            'filters': {'price': {
                'max': user.max_price,
                'min': user.min_price
            }}
        }

        hotels = api_request(url, payload, 'POST', message)

        amount_days = (user.check_out - user.check_in).days

        for i_hotel in hotels['data']['propertySearch']['properties']:
            hotel_info = dict()
            hotel_info['id'] = i_hotel['id']
            hotel_info['name'] = i_hotel['name']
            hotel_info['price'] = i_hotel['price']['lead']['amount']
            hotel_info['total price'] = hotel_info['price'] * amount_days
            hotel_info['distance to center'] = \
                i_hotel['destinationInfo']['distanceFromDestination']['value']

            user.hotel_list.append(hotel_info)

    except Exception:
        error_message(message)


def hotel_details(user: Users, hotel_id: int, message: Message) -> Tuple:
    """
    Функция, которая обрабатывает ответ запроса
    и получает дополнительные данные по отелям.

    :param user: передается пользователь.
    :param hotel_id: передается id отеля.
    :param message: передается сообщение чата телеграмм-бота.
    :return: возвращает кортеж с адресом и списком url фото.
    """
    try:
        url = "https://hotels4.p.rapidapi.com/properties/v2/detail"

        payload = {
            "currency": config.CURRENCY,
            "eapid": 1,
            "locale": config.LOCALE,
            "siteId": 300000001,
            "propertyId": hotel_id
        }

        hotel_data = api_request(url, payload, 'POST', message)

        hotel_detail = hotel_data['data']['propertyInfo']
        photo = list()
        count = 0

        if hotel_detail:
            address = \
                hotel_detail['summary']['location']['address']['addressLine']
            if user.photo_hotels:
                for i_url in hotel_detail['propertyGallery']['images']:
                    if count < user.photo_hotels:
                        photo.append(i_url['image']['url'])
                        count += 1
                    else:
                        break
            return address, photo
        else:
            raise ValueError

    except Exception:
        error_message(message)
        return 'error', ['https://disk.yandex.ru/i/TZ5v6qnX4HR7TQ']
