import telebot
import data.dataLoader as Dl
import data.myFunctions as Mf
import data.botInstruments as Bi
import data.markups as mark
import data.markupOptions as Op
import threading

functions = Mf.MyFunctions()

bot = telebot.TeleBot('А токена то нет :))))')


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Помощник для студента ОКЭИ и не только.\nПолный список команд: /help")
    bot.send_message(
        message.chat.id,
        "Рекомендуется перед началом выбрать группу: /group",
    )


@bot.message_handler(commands=['help'])
def command_help(message):
    bot.reply_to(message,
                 """Список команд:
/start - Запуск бота
/help - Список команд
/group - Действия с группой
/schedule - Узнать расписание
/info - Информация о пользователе
/calls - О расписании звонков
""")


@bot.message_handler(commands=['get'])
def admin_command_get(message):
    if not Dl.is_admin(message.from_user.id):
        Bi.unsigned_command(message.chat.id, bot)
        return

    res = functions.type_of(message.text, 'str')
    if res:
        if res[0] == 'get_groups_names':
            bot.send_message(message.chat.id, str(Dl.groups_names))
        if res[0] == 'update_groups_names':
            Dl.load_groups_names()
            bot.send_message(message.chat.id, 'update succesful')
        if res[0] == 'print':
            bot.send_message(message.chat.id, str(Dl.groups_users_names))


@bot.message_handler(commands=['admin'])
def admin_command_admin(message):
    if not Dl.is_admin(message.from_user.id):
        Bi.unsigned_command(message.chat.id, bot)
        return

    res = functions.type_of(message.text, 'str int')
    if res:
        if res[0] == 'add':
            res1 = Dl.add_admin(res[1])
            bot.reply_to(
                message,
                "Новый администратор." if res1 else "Пользователь уже является администратором."
            )
        elif res[0] == 'remove':
            res1 = Dl.remove_admin(res[1])
            bot.reply_to(
                message,
                "Администратор удален." if res1 else "Пользователь не администратор."
            )
        elif res[0] == 'is':
            res1 = Dl.is_admin(res[1])
            bot.reply_to(
                message,
                "Пользователь является администратором." if res1 else "Пользователь не является администратором."
            )


@bot.message_handler(commands=['group'])
def group_command(message):
    bot.send_message(
        message.chat.id,
        "Выберите группу, от которой получать расписание: ",
        reply_markup=mark.SET_GROUP,
    )


@bot.message_handler(commands=['info'])
def info_command(message):
    texts = ['Информация: ']
    texts += [f"Группа: {Dl.get_user_group(message.chat.id)}"]
    if Dl.is_admin(message.from_user.id):
        texts += ['Пользователь, вызвавший команду, владеет правами администратора бота.']

    bot.send_message(
        message.chat.id,
        '\n'.join(texts)
    )


@bot.message_handler(commands=['schedule'])
def schedule_command(message):
    if Dl.has_user_group(message.chat.id):
        bot.send_message(
            message.chat.id,
            "Узнать расписание:",
             reply_markup=mark.SCHEDULE,
        )
    else:
        bot.send_message(
            message.chat.id,
            "Перед тем, как узнать расписание, выберите группу: /group"
        )


@bot.message_handler(commands=['calls'])
def calls_schedule_command(message):
    bot.send_message(
        message.chat.id,
        "Выберите опцию:",
         reply_markup=mark.CALLS,
    )


@bot.message_handler(commands=['teacher'])
def teacher_command(message):
    bot.send_message(
        message.chat.id,
        "Выберите преподавателя, чтобы узнать его расписание (с сайта): ",
        reply_markup=mark.GET_TEACHER,
    )


@bot.message_handler(func=lambda message: True)
def get_text_messages(message):
    if message.text.startswith('/'):
        Bi.unsigned_command(message.chat.id, bot)
        return


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == Op.GO_TO_GROUP_START:
        bot.send_message(
            call.message.chat.id,
            "Выберите группу, от которой получать расписание: ",
            reply_markup=mark.SET_GROUP,
        )
    elif call.data.startswith(Op.GROUP_INDEXES):
        group_name = call.data[len(Op.GROUP_INDEXES):]
        if group_name in Dl.groups_names:
            Dl.set_user_group(call.message.chat.id, group_name)

            bot.send_message(
                call.message.chat.id,
                f"Установлена группа по умолчанию: {group_name}",
            )
            bot.delete_message(call.message.chat.id, call.message.message_id)

    elif call.data == Op.GET_SCHEDULE_TODAY:
        if not Dl.has_user_group(call.message.chat.id):
            bot.send_message(call.message.chat.id, "Перед тем, как узнать расписание, выберите группу: /group")
            return

        group_id = Dl.get_user_group(call.message.chat.id)
        indexes = Dl.get_day_indexes(Dl.today())
        if indexes is not None:
            schedule_list = list(Dl.schedule_excel[group_id][indexes[0]:indexes[1]])
            if not (len(schedule_list) == 0 or schedule_list.count('') == len(schedule_list)):
                schedule = '\n'.join(list(map(lambda x: str(x) if str(x) != 'nan' else '', schedule_list)))
                if not len(''.join(schedule.split())) == 0:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                    bot.send_message(
                        call.message.chat.id,
                        f"Расписание группы {group_id} сегодня (с сайта):{schedule}",
                        reply_markup=mark.TODAY_SCHEDULE
                    )
                    return
        bot.send_message(
            call.message.chat.id,
            f"На сегодня расписания для группы {group_id} нет.",
            reply_markup=mark.TODAY_SCHEDULE
        )
        bot.delete_message(call.message.chat.id, call.message.message_id)
    elif call.data == Op.GET_SCHEDULE_TOMORROW:
        if not Dl.has_user_group(call.message.chat.id):
            bot.send_message(call.message.chat.id, "Перед тем, как узнать расписание, выберите группу: /group")
            return

        group_id = Dl.get_user_group(call.message.chat.id)
        indexes = Dl.get_day_indexes(Dl.tomorrow())
        if indexes is not None:
            schedule_list = list(Dl.schedule_excel[group_id][indexes[0]:indexes[1]])
            if not (len(schedule_list) == 0 or schedule_list.count('') == len(schedule_list)):
                schedule = '\n'.join(list(map(lambda x: str(x) if str(x) != 'nan' else '', schedule_list)))
                if not len(''.join(schedule.split())) == 0:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                    bot.send_message(
                        call.message.chat.id,
                        f"Расписание группы {group_id} на завтра (с сайта):{schedule}",
                        reply_markup=mark.TODAY_SCHEDULE
                    )
                    return
        bot.send_message(
            call.message.chat.id,
            f"На завтра расписания для группы {group_id} нет.",
            reply_markup=mark.TODAY_SCHEDULE
        )
        bot.delete_message(call.message.chat.id, call.message.message_id)
    elif call.data == Op.GET_SCHEDULE_AT_DAY:
        bot.send_message(
            call.message.chat.id,
            "Узнать расписание:",
            reply_markup=mark.WEEK_DAYS
        )
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass

    elif call.data.startswith(Op.WEEK_DAYS_INDEXES):
        if not Dl.has_user_group(call.message.chat.id):
            bot.send_message(call.message.chat.id, "Перед тем, как узнать расписание, выберите группу: /group")
            return

        day = call.data[len(Op.WEEK_DAYS_INDEXES):]
        group_id = Dl.get_user_group(call.message.chat.id)
        indexes = Dl.get_day_indexes(day)
        if indexes is not None:
            schedule_list = list(Dl.schedule_excel[group_id][indexes[0]:indexes[1]])
            if not (len(schedule_list) == 0 or schedule_list.count('\n') == len(schedule_list)):
                schedule = '\n'.join(list(map(lambda x: str(x) if str(x) != 'nan' else '', schedule_list)))
                if not len(''.join(schedule.split())) == 0:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                    bot.send_message(
                        call.message.chat.id,
                        f"Расписание группы {group_id} на {day.lower()} (с сайта):{schedule}",
                        reply_markup=mark.WEEK_DAY_SCHEDULE
                    )
                    return
        bot.send_message(
            call.message.chat.id,
            f"{day}: расписания для группы {group_id} нет.",
            reply_markup=mark.WEEK_DAY_SCHEDULE
        )
        bot.delete_message(call.message.chat.id, call.message.message_id)
    elif call.data == Op.GO_TO_SCHEDULE_START:
        if not Dl.has_user_group(call.message.chat.id):
            bot.send_message(call.message.chat.id, "Перед тем, как узнать расписание, выберите группу: /group")
            return

        bot.edit_message_text(
            "Узнать расписание:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=mark.SCHEDULE
        )

    elif call.data == Op.GO_TO_CALLS:
        try: bot.edit_message_text(
            "Выберите опцию:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=mark.CALLS,
        )
        except Exception: pass
    elif call.data == Op.NEAREST_CALL:
        nearest_call = Dl.get_nearest_call()  # (8:30, '1 пара', 3)
        if nearest_call is not None:
            bot.send_message(
                call.message.chat.id,
                f"Ближайший звонок в {nearest_call[0]} через {nearest_call[2]} минут ({nearest_call[1]}).",
                reply_markup=mark.GO_TO_CALLS
            )
        else:
            bot.send_message(
                call.message.chat.id,
                f"Не ожидается больше звонков сегодня.",
                reply_markup=mark.GO_TO_CALLS
            )
        bot.delete_message(call.message.chat.id, call.message.message_id)

    elif call.data == Op.PIN_NEAREST_CALL:
        nearest_call = Dl.get_nearest_call()
        message = None
        if nearest_call is not None:
            message = bot.send_message(
                call.message.chat.id,
                f"🔁 Ближайший звонок в {nearest_call[0]} через {nearest_call[2]} минут ({nearest_call[1]}).",
            )
        else:
            message = bot.send_message(
                call.message.chat.id,
                f"🔁 Не ожидается больше звонков сегодня."
            )
        try:
            bot.pin_chat_message(
                chat_id=call.message.chat.id,
                message_id=message.message_id,
                disable_notification=True
            )
            bot.send_message(
                call.message.chat.id,
                'Сообщение прикреплено. Каждые 5 минут сообщение обновляется.',
                reply_markup=mark.GO_TO_CALLS
            )
        except Exception:
            bot.send_message(
                call.message.chat.id,
                'Ошибка прикрепления сообщения.',
                reply_markup=mark.GO_TO_CALLS
            )
        Dl.add_pinned_call((str(call.message.chat.id), str(message.message_id)))
        bot.delete_message(call.message.chat.id, call.message.message_id)
    elif call.data == Op.CALLS_TODAY:
        day = 'Понедельник' if Dl.today() == 'Понедельник' else 'Будни+суббота'
        text = '\n'.join([f'{k}: {v[0]} - {v[1]}' for k, v in Dl.call_schedule[day].items()])
        bot.send_message(
            call.message.chat.id,
            f"Расписание на сегодня: ({day}):\n{text}",
            reply_markup=mark.GO_TO_CALLS
        )
        bot.delete_message(call.message.chat.id, call.message.message_id)
    elif call.data == Op.CALLS_MONDAY:
        text = '\n'.join([f'{k}: {v[0]} - {v[1]}' for k, v in Dl.call_schedule['Понедельник'].items()])
        bot.send_message(
            call.message.chat.id,
            f"Расписание на понедельник:\n{text}",
            reply_markup=mark.GO_TO_CALLS
        )
        bot.delete_message(call.message.chat.id, call.message.message_id)
    elif call.data == Op.CALLS_ANOTHER_DAY:
        text = '\n'.join([f'{k}: {v[0]} - {v[1]}' for k, v in Dl.call_schedule['Будни+суббота'].items()])
        bot.send_message(
            call.message.chat.id,
            f"Расписание на будни/субботу:\n{text}",
            reply_markup=mark.GO_TO_CALLS
        )
        bot.delete_message(call.message.chat.id, call.message.message_id)


def update_pinned(on_init=False):
    now_time = Dl.time()
    if not 7 < now_time[0] < 20 and not on_init:
        threading.Timer(600, update_pinned).start()
        return

    now = '.'.join(list(map(lambda x: str(x).rjust(2, '0'), now_time)))

    has_except = False
    for k, v in Dl.pinned_calls.copy().items():
        try:
            nearest_call = Dl.get_nearest_call()
            bot.edit_message_text(
                f"🔁 Ближайший звонок в {nearest_call[0]} через {nearest_call[2]} минут ({nearest_call[1]})." if nearest_call is not None else f"🔁 Не ожидается больше звонков сегодня. (Обновлено в {now}).",
                int(k), int(v)
            )
        except telebot.apihelper.ApiException as e:
            del Dl.pinned_calls[k]
            has_except = True

    if has_except:
        Dl.save_pinned_calls()

    print("Обновление таймера")
    threading.Timer(300, update_pinned).start()


update_pinned(True)

bot.polling()
