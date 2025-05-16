from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def unsigned_command(user_id, bot):
    bot.send_message(user_id, 'Неизвестная команда. Попробуйте ещё раз!')


def create_inline_keyboard(elements={}, row_width=2, back_button=[]):
    markup = InlineKeyboardMarkup(row_width=row_width)
    buttons = []
    for name, option in elements.items():
        buttons += [InlineKeyboardButton(name, callback_data=option)]
    markup.add(*buttons)
    if len(back_button) == 2:
        markup.add(InlineKeyboardButton(back_button[0], callback_data=back_button[1]))
    return markup