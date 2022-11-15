import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('TOKEN')
RAPID_API_KEY = os.getenv('API_KEY')
LOCALE = os.getenv('LOCALE')
CURRENCY = os.getenv('CURRENCY')
DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
    ('help', "Вывести справку"),
    ('lowprice', "Топ самых дешёвых отелей"),
    ('highprice', "Топ самых дорогих отелей"),
    ('beastdeal',
     "Топ отелей, наиболее подходящих по цене и расположению от центра"),
    ('history', "Истории поиска отелей")
)
