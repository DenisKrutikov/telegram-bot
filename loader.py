import telebot
from config_data import config


bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode='HTML')