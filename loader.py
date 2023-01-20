import logging
import telebot
import sqlite3
from config_data import config


bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode='HTML')
logger = telebot.logging
telebot.logging.basicConfig(
    filename='filename.log',
    level=logging.DEBUG,
    format=' [%(asctime)s - %(levelname)s] - %(message)s',
    encoding='UTF-8'
)

with sqlite3.connect('database/search_history.db') as sqlite_connection:
    cursor = sqlite_connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS history (
    user_id INTEGER,
    command TEXT NOT NULL,
    command_date datetime,
    city TEXT NOT NULL,
    hotels TEXT NOT NULL
    )'''
                   )
