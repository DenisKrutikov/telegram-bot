import json
import requests
from config_data import config
from loader import bot


timeout = 10
count_attempts = 0
headers = {
    "content-type": "application/json",
    "X-RapidAPI-Key": config.RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


def api_request():
    pass


def city_request(user):
    url = 'https://hotels4.p.rapidapi.com/locations/v3/search'

    querystring = {'q': user.city, 'locale': config.LOCALE}

    response = requests.get(
        url=url,
        headers=headers,
        params=querystring,
        timeout=timeout
    )
    city = json.loads(response.text)
    with open('city2.json', 'w', encoding='utf-8') as file:
        json.dump(city, file, indent=4, ensure_ascii=False)

    for i in city['sr']:
        if i['type'] == 'CITY' and i['regionNames']['shortName'].lower() == user.city.lower():
            user.city_id = i['gaiaId']


