import pandas as pd

from datetime import datetime

from telegram import ReplyKeyboardMarkup

from free_time import free_time, tomorrow

def handle_text(update, context, user_triger, engine, statistics, name_kids, data_kids):
    if 'хочу похвалу' == update.message.text.lower() or 'skill' == update.message.text.lower():
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        reply_keyboard = [['Отменить']]
        if 'skill' == update.message.text.lower():
            skill = True
            sms = "Напиши родителям о своих новых умениях (навыках), они обязательно это заметят и оценят по достоинству. Родителям будет очень приятно узнать о твоих стараниях и результатах"
        else:
            skill = False
            sms = "Напиши родителям о своих достижениях, они обязательно это заметят и оценят по достоинству. Может писать хоть каждый час. Родителям будет очень приятно узнать о твоих стараниях и результатах"
        context.bot.send_message(chat_id=update.effective_chat.id, text=sms,
                                 reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                  one_time_keyboard=False))
        user_triger[update.effective_chat.id] = {
            "triger": 'i_want_praise',
            "skill": skill
        }
    elif 'статистика' == update.message.text.lower():
        reply_keyboard = [['по лайкам', 'по свободному времени'], ['статистика за год'], ['Отменить']]
        sms = 'Выберите какую статистику тебе вывести "по лайкам" или "по свободному времени"?'
        context.bot.send_message(chat_id=update.effective_chat.id, text=sms,
                                 reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                  one_time_keyboard=False))
    elif 'по лайкам' == update.message.text.lower():
        statistics(update, context)
    elif 'по свободному времени' == update.message.text.lower():
        reply_keyboard = [['за день', 'за неделю'], ['Отменить']]
        sms = 'За какой промежуток времени хочишь получить список свободного времени ребенка?'
        context.bot.send_message(chat_id=update.effective_chat.id, text=sms,
                                 reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                  one_time_keyboard=False))
    elif 'за день' == update.message.text.lower() or 'за неделю' == update.message.text.lower():
        week = False
        info = pd.read_sql(f"SELECT name FROM user_family WHERE user_id = '{update.effective_chat.id}';", engine)
        name = info.loc[0, "name"]
        if 'за неделю' == update.message.text.lower():
            week = True
        context.bot.send_message(chat_id=update.effective_chat.id, text=free_time(data_kids[name], name, week))
    elif "сообщить о проблеме" == update.message.text.lower():
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        reply_keyboard = [['Отменить']]
        sms = "Опишите проблему. Я передам Владимиру и при необходимости напомню, чтобы он не забыл"
        context.bot.send_message(chat_id=update.effective_chat.id, text=sms,
                                 reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                  one_time_keyboard=False))
        user_triger[update.effective_chat.id] = {
            "triger": 'problem'
        }
    elif "мой список дел" == update.message.text.lower():
        sms = ''
        user_triger[update.effective_chat.id] = {
            "triger": "case",
            "case_id": {},
            "name": "None",
            "close": False,
            "cancel": False,
            "choice": False
        }
        info = pd.read_sql_query(
            f"SELECT id, name_case, num_of_likes FROM list_cases WHERE repeated_date <= '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}' AND name = '{name_kids[update.effective_chat.id]}';",
            engine)
        if len(info) != 0:
            for i in range(len(info)):
                sms += f"{i + 1}) {info.loc[i, 'name_case']} - награда {info.loc[i, 'num_of_likes']}👍\n"
                user_triger[update.effective_chat.id]["case_id"][i + 1] = info.loc[i, 'id']
            reply_keyboard = [['завершить выполнение'], ['отменить выполнение'], ['выбрать еще...'],
                              ['Вернуться в главное меню']]
            context.bot.send_message(chat_id=update.effective_chat.id, text=sms,
                                     reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                      one_time_keyboard=False))
        else:
            sms = "Дел нет."
            reply_keyboard = [['Выбрать задание'],
                              ['Вернуться в главное меню']]
            context.bot.send_message(chat_id=update.effective_chat.id, text=sms,
                                     reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                      one_time_keyboard=False))
        info2 = pd.read_sql_query(f"SELECT every_day FROM user_family WHERE user_id = '{update.effective_chat.id}';",
                                  engine)
        likes = int(tomorrow(data_kids[name_kids[update.effective_chat.id]], True, 0)) - int(info2.loc[0, 'every_day'])
        if likes > 0:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Сегодня осталось получить {likes} лайков")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Сегодня набраны все лайки.\n")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Я Вас не понимаю.")