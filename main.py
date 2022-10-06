from Users.user_info import Users
from handlers.hotel_price import get_photo_hotels
from handlers.hotel_price import start_search
from handlers.hotel_price import result
from loader import bot


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.from_user.id, text='Здравствуйте, {name}'.format(name=message.from_user.first_name))
    bot.send_message(message.from_user.id, text='Я помогу тебе подобрать отель')


@bot.message_handler(commands=['lowprice'])
def low_price(message):
    user = Users.get_user(message.from_user.id)
    user.command = 'lowprice'
    start_search(message, 'PRICE')


@bot.message_handler(commands=['highprice'])
def high_price(message):
    user = Users.get_user(message.from_user.id)
    user.command = 'highprice'
    start_search(message, 'PRICE_HIGHEST_FIRST')


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'yes':
        msg = bot.send_message(chat_id=call.message.chat.id, text='Сколько фото показать? (не больше 10)')
        bot.register_next_step_handler(msg, get_photo_hotels)
    if call.data == 'no':
        result(call)
    bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.from_user.id, text='Привет, чем я могу тебе помочь?')
    else:
        bot.send_message(message.from_user.id, text='Я тебя не понимаю.')


if __name__ == '__main__':
    bot.polling(none_stop=True)