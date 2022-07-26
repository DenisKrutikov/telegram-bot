import telebot
import subprocess
import consts

subprocess.check_call(['attrib', '+H', 'consts.py'])
bot = telebot.TeleBot(consts.token)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == 'Привет':
        bot.send_message(message.from_user.id, 'Привет, чем я могу тебе помочь?')
    elif message.text == '/hello_world':
        bot.send_message(message.from_user.id, 'Напиши привет')
    else:
        bot.send_message(message.from_user.id, 'Я тебя не понимаю.')


bot.polling(none_stop=True)