import pandas as pd
import pickle
import logging

from datetime import datetime, timedelta
from threading import Thread

from apiclient import discovery
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


from free_time import tomorrow

working_folder = "" #'/home/menace134/py/family/'

# logging.basicConfig(filename=working_folder + 'bot_v3.log',
#                     filemode='a',
#                     level=logging.INFO,
#                     format='%(asctime)s %(process)d-%(levelname)s %(message)s',
#                     datefmt='%d-%b-%y %H:%M:%S')

def finder(update,context,name,ru_name, engine):
    credentials = pickle.load(open(f"{working_folder}calendar_tokens/token_{name}.pkl", "rb"))
    service = discovery.build("calendar", "v3", credentials=credentials, cache_discovery=False)
    ################## Get My Calendars ###################
    result = service.calendarList().list().execute()
    ##################### Get My Calendar Events #####################
    calendar_id = result['items'][0]['id']
    result = service.events().list(calendarId=calendar_id, timeZone="Europe/Moscow", singleEvents=True,orderBy="startTime",timeMin=datetime.now().strftime("%Y-%m-%dT00:00:00+03:00"),timeMax=datetime.now().strftime("%Y-%m-%dT23:59:59+03:00")).execute()
    if result['items'] == []:
        print(result['items'])
        context.bot.send_message(chat_id=update.effective_chat.id,text = "В расписании ничего не заполнено на текущий день")
    else:
        print(result['items'])
        now = datetime.now().strftime("%Y-%m-%dT%H:%M:00+03:00")
        nowDate = datetime.now().strftime("%Y-%m-%d")
        nowTime = datetime.now().strftime("%H:%M:00")
        start = []
        end = []
        try:
            start_time = '08:00:00'
            end_time = '23:59:59'
            TimeOut = True
            for i in range(len(result['items'])):
                if "start" in result['items'][i] and 'summary' in result['items'][i]:
                    date_start = str(result['items'][i]['start']['dateTime'])
                    date_end = str(result['items'][i]['end']['dateTime'])
                    if date_start.split("T")[0] == nowDate:  # сверяем дату событий и выбираем только сегодня.
                        time = date_start[:19].split("T")[1]
                        time2 = date_end[:19].split("T")[1]
                        start += [time]
                        end += [time2]
                        if now >= date_start and now <= date_end:
                            text = str(ru_name) + " сейчас находится на занятии \"" + str(result['items'][i]['summary']) + "\". Время занятия с " + str(time)[:5] + " по " + str(time2)[:5] + "."
                            context.bot.send_message(chat_id=update.effective_chat.id, text=text)
                            logging.info(result['items'][i]['summary'])
                            logging.info('start = ' + time)
                            logging.info('end = ' + time2)
                            TimeOut = False
                        else:
                            # ищем начало перервыва это конец урока
                            if start_time <= time2 and nowTime >= time2:
                                start_time = time2
                            # ищем конец перервыва это начало урока
                            if end_time >= time and nowTime <= time:
                                end_time = time
            if TimeOut:
                if max(end) >= nowTime:
                    logging.info('Начало перерыва = ' + start_time)
                    logging.info('Конец перерыва = ' + end_time)
                    timeout = datetime.strptime(end_time, "%H:%M:%S") - datetime.strptime(start_time, "%H:%M:%S")
                    timeout_OFF = datetime.strptime(end_time, "%H:%M:%S") - datetime.strptime(nowTime, "%H:%M:%S")
                    logging.info("время перерыва = " + str(timeout))
                    logging.info("До конца перерыва осталось " + str(timeout_OFF))
                    text = f"{str(ru_name)} - по графику перерыв с {str(start_time)[:5]} до {str(end_time)[:5]}\nВремя перерыва {str(timeout)}\nДо конца перерыва осталось {str(timeout_OFF)}"
                else:
                    answer = pd.read_sql_query(f"SELECT answer, comment FROM user_family WHERE name = '{ru_name}';",engine)
                    if ru_name == "Вова":
                        go = "пошел"
                        answer_text = "ответил"
                    else:
                        go = "пошла"
                        answer_text = "ответила"
                    if answer.loc[0,"answer"] == 0:

                        text = f"{str(ru_name)}, на запрос еще не {answer_text}, но занятие закончилось в {max(end)[:5]}."
                    elif answer.loc[0, "answer"] == 1:
                        text = str(ru_name) + ", cейчас дома."
                    elif answer.loc[0, "answer"] == 2:
                        if answer.loc[0, "comment"] != "None" and answer.loc[0, "comment"] is not None:
                            logging.info(f"{ru_name} не {go} домой. На вопрос почему, {answer_text}: \"{answer.loc[0, 'comment']}\"")
                            text=f"{ru_name} не {go} домой. На вопрос почему, {answer_text}: \"{answer.loc[0, 'comment']}\""
                        else:
                            logging.info(f"{ru_name} не {go} домой. На вопрос почему, ответа не поступило.")
                            text=f"{ru_name} не {go} домой. На вопрос почему, ответа не поступило."
                        #text = f"{str(ru_name)}, на запрос {answer_text}, но занятия закончились в {max(end)}."
                context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        except Exception as err:
            logging.error(" Ошибка в функции \"finder()\": " + str(err))

def statistics_book(update, context, Timer_status, engine): # функция для вывода информации о том что сейчас читают дети
    # Берем из базы данны списоккниг которые еще не прочитали (у них статус 0)
    info = pd.read_sql_query(f"SELECT name, writer, book_name, all_page, every_day_page, old_page, new_page FROM books WHERE status = '0' AND  name in ('Амира','Лиза','Вова','Лейла');",engine)
    # Будем все это дело записывать в словарь чтобы потом красиво вывести
    book_data = {
                "Амира": [],
                "Вова": [],
                "Лейла": [],
                "Лиза": []
                }
    text = ''
    # Собираем инфу
    for i in range(len(info)):
        book_data[f"{info.loc[i,'name']}"]+=[[info.loc[i,'writer'],info.loc[i,'book_name'],info.loc[i,'all_page'],info.loc[i,'every_day_page'],info.loc[i,'old_page'],info.loc[i,'new_page']]]
    # Складываем ранее записанную информацию в понятный для нас текст для дальнейшей отправки пользователю
    for name in book_data:
        if name == "Вова":
            stop = 'остановился'
            read = 'прочитал'
        else:
            stop = 'остановилась'
            read = 'прочитала'
        summa = 0.0
        text2 = ''
        for j in range(len(book_data[name])):
            new_page = int(book_data[name][j][5])
            old_page = int(book_data[name][j][4])
            every_day_page = int(book_data[name][j][3])
            if new_page != 0 and old_page <= new_page:
                if every_day_page == 0:
                    norma = ((new_page - old_page) * 100)
                else:
                    norma = ((new_page - old_page) * 100) / every_day_page
                logging.info("norma = " + str(norma) + "%")
                summa += norma
                text2 +=f'{j+1}) {book_data[name][j][0]}({book_data[name][j][1]}), всего страниц "{book_data[name][j][2]}", {stop} на странице {new_page}, норма за день {every_day_page} стр.\n'
            else:
                text2 += f'{j+1}) {book_data[name][j][0]}({book_data[name][j][1]}), всего страниц "{book_data[name][j][2]}", {stop} на странице {old_page}, норма за день {every_day_page} стр.\n'
        text += f"- {name} {read} {int(summa + (0.5 if summa > 0 else -0.5))}% от нормы за день.\n{text2}\n"
    # Выводим пользователю всю информацию
    context.bot.send_message(chat_id=update.effective_chat.id,text=text)
    # Ждем минуту и удаляем текст,чтобы не мешал
    Thread(target=Timer_status, args=(update, context, 60, update.message.message_id+1)).start()

def statistics_end_book(update, context, Timer_status, engine):
    print(f"year = {datetime.now().year}")
    info = pd.read_sql_query(f"SELECT name, writer, book_name, all_page FROM books WHERE status = 'прочитано' AND year_final ='{datetime.now().year}' AND  name in ('Прочитано(Амира)','Прочитано(Лиза)','Прочитано(Вова)','Прочитано(Лейла)');",engine)
    if len(info) != 0:
        book_data = {
                    "Амира": [],
                    "Вова": [],
                    "Лейла": [],
                    "Лиза": []
                    }
        text = ''
        for i in range(len(info)):
            name = str(info.loc[i,'name']).replace("Прочитано(","").replace(")","")
            book_data[f"{name}"] += [[info.loc[i,'writer'],info.loc[i,'book_name'],info.loc[i,'all_page']]]
        for name in book_data:
            if name == "Вова":
                read = 'прочитал'
            else:
                read = 'прочитала'
            text2 = ''
            for j in range(len(book_data[name])):
                text2 += f'{j+1}) {book_data[name][j][0]}({book_data[name][j][1]}), всего страниц "{book_data[name][j][2]}"\n'
            if text2 != '':
                text += f"- {name} {read}:\n{text2}\n"
    else:
        text = 'В этом году не было прочитано ни одной книги.'
    context.bot.send_message(chat_id=update.effective_chat.id,text=text)
    Thread(target=Timer_status, args=(update, context, 60, update.message.message_id+1)).start()

def handle_text(update, context, user_triger, engine, statistics, Timer_status, kids, data_kids):
    if 'амира' == update.message.text.lower():
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        finder(update, context, "Amira", "Амира", engine)
    elif 'лиза' == update.message.text.lower():
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        finder(update, context, "Lisa", "Лиза", engine)
    elif 'лейла' == update.message.text.lower():
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        finder(update, context, "Leila", "Лейла", engine)
    elif 'вова' == update.message.text.lower():
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        finder(update, context, "Vova", "Вова", engine)
    elif 'оценить' == update.message.text.lower():
        reply_keyboard = [['Оценить поступок', 'Оценить "skill" детей'], ['Отменить']]
        sms = 'Выберите "Оценить поступок" или "Оценить "skill" детей"'
        context.bot.send_message(chat_id=update.effective_chat.id, text=sms,
                                 reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                  one_time_keyboard=False))
    elif 'статистика' == update.message.text.lower():
        reply_keyboard = [['по лайкам', 'по книгам'], ['статистика за год'], ['свободное время ребенка'], ['Отменить']]
        sms = 'Выберите какую статистику Вам вывести "по лайкам" или "по книгам"?'
        context.bot.send_message(chat_id=update.effective_chat.id, text=sms,
                                 reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                  one_time_keyboard=False))
    elif 'по лайкам' == update.message.text.lower():
        statistics(update, context)
    elif 'по книгам' == update.message.text.lower():
        reply_keyboard = [['прочитано', 'читают'], ['Отменить']]
        sms = 'Вывести на экран все что "прочитано" или "читают"?'
        context.bot.send_message(chat_id=update.effective_chat.id, text=sms,
                                 reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                  one_time_keyboard=False))
    elif 'читают' == update.message.text.lower():
        statistics_book(update, context, Timer_status, engine)
    elif 'прочитано' == update.message.text.lower():
        statistics_end_book(update, context, Timer_status, engine)
    elif 'свободное время ребенка' == update.message.text.lower():
        reply_keyboard = [['за день', 'за неделю'], ['Отменить']]
        sms = 'За какой промежуток времени Вы хотите получить список свободного времени ребенка?'
        context.bot.send_message(chat_id=update.effective_chat.id, text=sms,
                                 reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                  one_time_keyboard=False))
    elif 'за день' == update.message.text.lower() or 'за неделю' == update.message.text.lower():
        week = False
        if 'за неделю' == update.message.text.lower():
            week = True
        user_triger[update.effective_chat.id] = {
            'triger': 'free_time',
            'week': week,
        }
        sms = f"Выбирете ребенка."
        reply_keyboard = [['Амира', 'Лиза'], ['Лейла', 'Вова'], ['Отменить']]
        context.bot.send_message(chat_id=update.effective_chat.id, text=sms,
                                 reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                  one_time_keyboard=False))
    elif "сообщить о проблеме" == update.message.text.lower():
        reply_keyboard = [['сообщить', 'список проблем'], ['Отменить']]
        sms = 'Выберите, "сообщить о проблеме" или вывести "список проблем"??'
        context.bot.send_message(chat_id=update.effective_chat.id, text=sms,
                                 reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                  one_time_keyboard=False))
    elif "сообщить" == update.message.text.lower():
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        reply_keyboard = [['Отменить']]
        sms = "Опишите проблему. Я передам Владимиру и при необходимости напомню, чтобы он не забыл"
        context.bot.send_message(chat_id=update.effective_chat.id, text=sms,
                                 reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                  one_time_keyboard=False))
        user_triger[update.effective_chat.id] = {
            "triger": 'problem'
        }
    elif 'оценить поступок' == update.message.text.lower() or 'оценить "skill" детей' == update.message.text.lower():
        skill = False
        reply_keyboard = [['Амиру', 'Лизу'], ['Лейлу', 'Вову'], ['Отменить']]
        context.bot.send_message(chat_id=update.effective_chat.id, text="Кого будем оценивать?",
                                 reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                  one_time_keyboard=False))
        if 'оценить "skill" детей' == update.message.text.lower():
            skill = True
        user_triger[update.effective_chat.id] = {
            "triger": 'assess',
            "skill": skill,
            "name": "None",
            "choice": "None",
            "text": "None"
        }
    elif 'хотят похвалу' == update.message.text.lower():
        reply_keyboard = [['...за поступок', '...за "skill"'], ['Вернуться в главное меню']]
        sms = "Какой список Вам предоставить?"
        context.bot.send_message(chat_id=update.effective_chat.id, text=sms,
                                 reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                  one_time_keyboard=False))
    elif '...за поступок' == update.message.text.lower() or '...за "skill"' == update.message.text.lower():
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        sms = ''
        time1 = datetime.now() - timedelta(weeks=+1)
        info = pd.read_sql_query(
            f"SELECT name, msg_text, date, kids FROM msg_list WHERE date > '{time1}' ORDER BY date ASC;",
            engine)  #
        if '...за поступок' == update.message.text.lower():
            yes = "yes"
            sms_false = 'за поступок'
        elif '...за "skill"' == update.message.text.lower():
            yes = "IQ_Yes"
            sms_false = ' за "skill"'
        if len(info) != 0:
            for i in range(len(info)):
                if info.loc[i, 'kids'] == yes:
                    if i != 60:
                        sms += str(info.loc[i, 'date'].strftime('%d.%m.%Y %H:%M')) + " " + str(
                            info.loc[i, 'name']) + ':\n"' + str(info.loc[i, 'msg_text']) + '"\n\n'
                    else:
                        context.bot.send_message(chat_id=update.effective_chat.id, text=sms)
                        sms = ''
            if sms != '':
                context.bot.send_message(chat_id=update.effective_chat.id, text=sms)
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Никто не хочет похвалу" + sms_false)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Никто не хочет похвалу" + sms_false)
    elif 'список дел...' == update.message.text.lower():
        reply_keyboard = [['... на выполнении у детей', '... выполненые', '... не выполненые'],
                          ['Вернуться в главное меню']]
        sms = "Какой список Вам предоставить?"
        context.bot.send_message(chat_id=update.effective_chat.id, text=sms,
                                 reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                  one_time_keyboard=False))
        info = pd.read_sql_query(
            f"SELECT name, every_day FROM user_family WHERE user_id in ('1933394156','462169878','2133224553','1477410591');",
            engine)
        text = ''
        for j in range(4):
            print(j)
            likes = int(tomorrow(data_kids[str(info.loc[j, 'name'])], True, 0)) - int(info.loc[j, 'every_day'])
            if likes > 0:
                text += f"{info.loc[j, 'name']}: Сегодня осталось получить {likes} лайков.\n"
            else:
                text += f"{info.loc[j, 'name']}: Сегодня набраны все лайки.\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    elif '... на выполнении у детей' == update.message.text.lower():
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        sms = ''
        for name in kids:
            info = pd.read_sql_query(f"SELECT name_case, num_of_likes FROM list_cases WHERE name = '{name}';", engine)
            if len(info) != 0:
                sms += name + ':\n'
                for i in range(len(info)):
                    sms += f"{i + 1}) {info.loc[i, 'name_case']} - награда {info.loc[i, 'num_of_likes']}👍\n"
                    if i == len(info) - 1:
                        sms += '\n'
        context.bot.send_message(chat_id=update.effective_chat.id, text=sms)
    elif '... выполненые' == update.message.text.lower():
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        info = pd.read_sql_query(
            f"SELECT id, name_case, num_of_likes FROM list_cases WHERE repeated_date > '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}' AND name = '0';",
            engine)
        sms = ''
        for i in range(len(info)):
            sms += f"{i + 1}) {info.loc[i, 'name_case']} - награда {info.loc[i, 'num_of_likes']}👍\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=sms)
    elif '... не выполненые' == update.message.text.lower() or 'выбрать задание' == update.message.text.lower():
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        info = pd.read_sql_query(
            f"SELECT id, name_case, num_of_likes FROM list_cases WHERE repeated_date <= '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}' AND name = '0';",
            engine)
        sms = ''
        for i in range(len(info)):
            sms += f"{i + 1}) {info.loc[i, 'name_case']} - награда {info.loc[i, 'num_of_likes']}👍\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=sms)
    elif 'список для покупки' == update.message.text.lower():
        info = pd.read_sql(f"SELECT categories, products, quantity, name, order_date FROM shopping_list WHERE order_date = '{datetime.now().strftime('%d.%m.%Y')}' ORDER BY products, quantity DESC;", engine)
        sms = ''
        link_sms = ''
        list_antidubles = []
        k=0
        for i in range(len(info)):
            if f"{info.loc[i, 'products']}" not in list_antidubles:
                k += 1
                sms += f"{k}) {info.loc[i, 'products']} необходимо купить - {info.loc[i, 'quantity']}шт. ({info.loc[i, 'name']})\n"
                link_db = pd.read_sql_query(f"SELECT link FROM products WHERE name = '{str(info.loc[i, 'products']).replace('%','%%')}';",engine)
                link_sms += f"{k}) {link_db.loc[0, 'link']}\n"
                list_antidubles += [f"{info.loc[i, 'products']}"]
        context.bot.send_message(chat_id=update.effective_chat.id, text=sms + '\n\n' + link_sms)
    elif 'повторить опрос для покупок' == update.message.text.lower():
        categories = pd.read_sql(f"SELECT * FROM categories;", engine)
        info = pd.read_sql(f"SELECT name, user_id FROM user_family WHERE access in ('0','1');", engine)
        list_categories = []
        keyboard = []
        for k in range(len(categories)):
            if categories.loc[k, 'frequency'] == categories.loc[k, 'num_day']:
                list_categories += [categories.loc[k, 'name']]
        for j in range(len(list_categories)):
            keyboard += [[InlineKeyboardButton(list_categories[j],
                                               callback_data='query_for_buy_products-' + str(list_categories[j]))]]
        if len(keyboard) > 1:
            sms = "Что-нибудь из данных категорий необходимо приобрести?"
        elif len(keyboard) == 0:
            return
        else:
            sms = "Что-нибудь из данной категории необходимо приобрести?"
        for i in range(len(info)):
            if info.loc[i, 'name'] != 'Вова': #info.loc[i, 'name'] != 'Константин' or 
                try:
                    context.bot.send_message(chat_id=info.loc[i, 'user_id'], text=sms, reply_markup=InlineKeyboardMarkup(keyboard))
                except Exception:
                    logging.error(f"не могу отправить опрос на продукты chat_id={info.loc[i, 'user_id']}")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Я Вас не понимаю.")