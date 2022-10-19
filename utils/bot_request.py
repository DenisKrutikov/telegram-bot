import json
import requests
from config_data import config
from loader import bot

timeout = 15
headers = {
    "X-RapidAPI-Key": config.RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


def api_request(url, querystring, message):
    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=timeout)
        return json.loads(response.text)
    except requests.exceptions.ReadTimeout:
        bot.send_message(message.from_user.id, text='Ошибка запроса API.')
