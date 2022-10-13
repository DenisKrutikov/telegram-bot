import datetime

from telebot.types import ReplyKeyboardRemove

from handlers.best_deal import start_search_bd, get_photo_hotels_bd, result_bd
from users.user_info import Users
from handlers.hotel_price import get_photo_hotels, get_number_hotels
from handlers.hotel_price import start_search
from handlers.hotel_price import result
from loader import bot
from utils.bot_methods import calendar, calendar_1_callback, add_calendar


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.from_user.id, text='Здравствуйте, {name}'.format(name=message.from_user.first_name))
    bot.send_message(message.from_user.id, text='Я помогу тебе подобрать отель')


@bot.message_handler(commands=['lowprice'])
def low_price(message):
    user = Users.get_user(message.from_user.id)
    user.command = '/lowprice'
    start_search(message)


@bot.message_handler(commands=['highprice'])
def high_price(message):
    user = Users.get_user(message.from_user.id)
    user.command = '/highprice'
    start_search(message)


@bot.message_handler(commands=['beastdeal'])
def beast_deal(message):
    user = Users.get_user(message.from_user.id)
    user.command = '/beastdeal'
    start_search_bd(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_1_callback.prefix))
def callback_inline(call):
    user = Users.get_user(call.from_user.id)
    name, action, year, month, day = call.data.split(calendar_1_callback.sep)
    date = calendar.calendar_query_handler(bot=bot, call=call, name=name, action=action, year=year, month=month, day=day)

    if action == "DAY":
        if date < datetime.datetime.now():
            bot.send_message(call.from_user.id,
                             text=f'Ошибка. Дата не может быть меньше сегодняшней.\n '
                                  f'Выберите дату заезда.',
                             reply_markup=add_calendar(call.message)
                             )
            return
        elif user.check_in is not None and date < user.check_in:
            bot.send_message(call.from_user.id,
                             text=f'Ошибка. Дата не может быть меньше даты заезда.\n '
                                  f'Выберите дату выезда".',
                             reply_markup=add_calendar(call.message)
                             )
            return
        bot.send_message(
            chat_id=call.from_user.id,
            text=f"Вы выбрали: {date.strftime('%d.%m.%Y')}",
            reply_markup=ReplyKeyboardRemove()
        )
        if user.action == 'check_in':
            user.check_in = date
            bot.send_message(call.from_user.id, text='Выберите дату выезда.', reply_markup=add_calendar(call.message))
            user.action = 'check_out'
        else:
            user.check_out = date
            msg = bot.send_message(call.from_user.id, text='Напиши количество отелей (не больше 10)')
            bot.register_next_step_handler(msg, get_number_hotels)

    elif action == "CANCEL":
        bot.send_message(
            chat_id=call.from_user.id,
            text="Cancellation",
            reply_markup=ReplyKeyboardRemove()
        )


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    user = Users.get_user(call.from_user.id)
    if call.data == 'yes':
        msg = bot.send_message(chat_id=call.message.chat.id, text='Сколько фото показать? (не больше 10)')
        if user.command == '/beastdeal':
            bot.register_next_step_handler(msg, get_photo_hotels_bd)
        else:
            bot.register_next_step_handler(msg, get_photo_hotels)
    if call.data == 'no':
        if user.command == '/beastdeal':
            result_bd(call)
        else:
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
