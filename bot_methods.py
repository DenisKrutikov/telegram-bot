from telebot import types


def add_button(message, bot):
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Показать', callback_data='yes')
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text='Ненужно', callback_data='no')
    keyboard.add(key_no)
    bot.send_message(message.from_user.id, text='Показать фото отелей?', reply_markup=keyboard)



