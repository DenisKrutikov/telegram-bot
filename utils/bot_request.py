import requests

from config_data import config
from datetime import date, timedelta


timeout = 15
headers = {
    "X-RapidAPI-Key": config.RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


def city_request(city):
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring = {"query": city, "locale": "ru_RU", "currency": "RUB"}
    return requests.request("GET", url, headers=headers, params=querystring, timeout=timeout)


def hotels_request(user, sort_order):
    url = "https://hotels4.p.rapidapi.com/properties/list"
    today = date.today()
    tomorrow = today + timedelta(days=1)
    querystring = {
        "destinationId": user.city_id, "pageNumber": "1", "pageSize": user.hotels_count, "checkIn": today,
        "checkOut": tomorrow, "adults1": "1", "sortOrder": sort_order, "locale": "ru_RU", "currency": "RUB"
    }
    return requests.request("GET", url, headers=headers, params=querystring, timeout=timeout)


def hotels_request_bd(user):
    url = "https://hotels4.p.rapidapi.com/properties/list"
    today = date.today()
    tomorrow = today + timedelta(days=1)
    querystring = {
        "destinationId": user.city_id, "pageNumber": 1, "pageSize": user.hotels_count, "checkIn": today,
        "checkOut": tomorrow, "adults1": 1, "priceMin": user.min_price, "priceMax": user.max_price,
        "sortOrder": "DISTANCE_FROM_LANDMARK", "locale": "ru_RU", "currency": "RUB", "landmarkIds": "Центр города"
    }
    return requests.request("GET", url, headers=headers, params=querystring, timeout=timeout)


def photo_request(hotel):
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    querystring = {"id": hotel['id']}
    return requests.request("GET", url, headers=headers, params=querystring, timeout=timeout)