import os
import requests
from dotenv import load_dotenv
from datetime import date, timedelta


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

timeout = 15
headers = {
    "X-RapidAPI-Key": os.getenv('API_KEY'),
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


def city_request(city):
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring = {"query": city, "locale": "ru_RU", "currency": "RUB"}
    return requests.request("GET", url, headers=headers, params=querystring, timeout=timeout)


def hotels_request(city, sort_order):
    url = "https://hotels4.p.rapidapi.com/properties/list"
    today = date.today()
    tomorrow = today + timedelta(days=1)
    querystring = {
        "destinationId": city['destinationId'], "pageNumber": "1", "pageSize": city['number_hotels'], "checkIn": today,
        "checkOut": tomorrow, "adults1": "1", "sortOrder": sort_order, "locale": "ru_RU", "currency": "RUB"
    }
    return requests.request("GET", url, headers=headers, params=querystring, timeout=timeout)


def photo_request(hotel):
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    querystring = {"id": hotel['id']}
    return requests.request("GET", url, headers=headers, params=querystring, timeout=timeout)