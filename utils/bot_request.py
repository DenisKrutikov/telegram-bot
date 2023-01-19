import json
import requests
from config_data import config
from loader import bot

timeout = 10
headers = {
    "content-type": "application/json",
    "X-RapidAPI-Key": config.RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


def city_request(user, message):
    try:
        url = 'https://hotels4.p.rapidapi.com/locations/v3/search'

        querystring = {'q': user.city, 'locale': config.LOCALE}

        response = requests.get(
            url=url,
            headers=headers,
            params=querystring,
            timeout=timeout
        )
        city = json.loads(response.text)

        for i_city in city['sr']:
            if i_city['type'] == 'CITY' and i_city['regionNames']['shortName'].lower() == user.city.lower():
                user.city_id = i_city['gaiaId']
    except requests.exceptions.ReadTimeout:
        bot.send_message(
            message.from_user.id,
            text='Сервис не отвечает. Попробуйте позже.'
        )
    except TypeError:
        bot.send_message(
            message.from_user.id,
            text='Ошибка сервиса. Попробуйте еще раз.'
        )


def hotel_request(user, message):
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

        response = requests.post(
            url=url,
            json=payload,
            headers=headers,
            timeout=timeout
        )
        hotels = json.loads(response.text)

        amount_days = (user.check_out - user.check_in).days
        for i_hotel in hotels['data']['propertySearch']['properties']:
            hotel_info = dict()
            hotel_info['id'] = i_hotel['id']
            hotel_info['name'] = i_hotel['name']
            hotel_info['price'] = i_hotel['price']['lead']['amount']
            hotel_info['total price'] = hotel_info['price'] * amount_days
            hotel_info['distance to center'] = \
                i_hotel['destinationInfo']['distanceFromDestination']['value']
            hotel_detail = hotel_details(i_hotel['id'], message)
            hotel_info['address'] = \
                hotel_detail['summary']['location']['address']['addressLine']
            if user.photo_hotels:
                photo = list()
                count = 0
                for i_url in hotel_detail['propertyGallery']['images']:
                    if count < user.photo_hotels:
                        photo.append(i_url['image']['url'])
                        count += 1
                    else:
                        break
                hotel_info['photo'] = photo
            user.hotel_list.append(hotel_info)
    except requests.exceptions.ReadTimeout:
        bot.send_message(
            message.from_user.id,
            text='Сервис не отвечает. Попробуйте позже.'
        )
    except TypeError:
        bot.send_message(
            message.from_user.id,
            text='Ошибка сервиса. Попробуйте еще раз.'
        )


def hotel_details(hotel_id, message):
    try:
        url = "https://hotels4.p.rapidapi.com/properties/v2/detail"

        payload = {
            "currency": config.CURRENCY,
            "eapid": 1,
            "locale": config.LOCALE,
            "siteId": 300000001,
            "propertyId": hotel_id
        }

        response = requests.post(
            url=url,
            json=payload,
            headers=headers,
            timeout=timeout
        )
        hotel_data = json.loads(response.text)

        if hotel_data['data']['propertyInfo']:
            return hotel_data['data']['propertyInfo']
        else:
            raise ValueError

    except requests.exceptions.ReadTimeout:
        bot.send_message(
            message.from_user.id,
            text='Сервис не отвечает. Попробуйте позже.'
        )
    except ValueError:
        bot.send_message(
            message.from_user.id,
            text='Ошибка сервиса. Попробуйте еще раз.'
        )
