import logging
import telebot
from config_data import config


bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode='HTML')
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)