import telebot
import os
from dotenv import load_dotenv
from hotel_price import get_photo_hotels
from hotel_price import start_search
from hotel_price import result


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

bot = telebot.TeleBot(os.getenv('TOKEN'), parse_mode='HTML')


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.from_user.id, text='Здравствуйте, {name}'.format(name=message.from_user.first_name))
    bot.send_message(message.from_user.id, text='Я помогу тебе подобрать отель')


@bot.message_handler(commands=['lowprice'])
def low_price(message):
    start_search(message, bot, 'PRICE')


@bot.message_handler(commands=['highprice'])
def high_price(message):
    start_search(message, bot, 'PRICE_HIGHEST_FIRST')


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'yes':
        msg = bot.send_message(chat_id=call.message.chat.id, text='Сколько фото показать? (не больше 10)')
        bot.register_next_step_handler(msg, get_photo_hotels, bot)
    if call.data == 'no':
        result(call, bot)
    bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.from_user.id, text='Привет, чем я могу тебе помочь?')
    else:
        bot.send_message(message.from_user.id, text='Я тебя не понимаю.')


if __name__ == '__main__':
    bot.polling(none_stop=True)