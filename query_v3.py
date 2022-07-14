# coding=UTF-8
#
#
import pandas as pd
import logging
import pickle
import telegram

from apiclient import discovery
from work import TELEGRAM_TOKEN, ivea_family, papa, mama, kids, data_kids, working_folder
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import create_engine
from datetime import datetime
from threading import Thread
from time import sleep
from free_time import tomorrow

logging.basicConfig(filename=working_folder + 'log/query_test_'+ datetime.now().strftime('%d.%m.%Y') +'.log',
                    filemode='a',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%H:%M:%S')

bot = telegram.Bot(TELEGRAM_TOKEN) # Коннект по токену

engine = create_engine(ivea_family)  # данные для соединия с сервером

time_begin_and_end = {}

def begin(name,zan):# begin new day, new query
    info = pd.read_sql(f"SELECT user_id FROM user_family WHERE name ='{name}'", engine)
    keyboard = [[InlineKeyboardButton('Да', callback_data='YES-' + str(name)),
                 InlineKeyboardButton('Нет', callback_data='NO-' + str(name))]]
    if time < "12:00:00":
        text = f'Доброе утро!!! 😊 Родителям важно знать, что у тебя все в порядке. Ты успеваешь на {zan}?'
    else:
        text = f'Привет! 😊 Родителям важно знать, что у тебя все в порядке. Ты успеваешь на {zan}?'
    logging.info(f'{name}: Привет! Родителям важно знать, что у тебя все в порядке. Ты успеваешь на {zan}?')
    bot.send_message(chat_id=int(info.loc[0, "user_id"]), text=text, reply_markup=InlineKeyboardMarkup(keyboard))
    engine.execute(f"UPDATE user_family SET answer = 0, comment = 'None' WHERE name ='{name}'")

def start(name):  # совпадение означает что 10 мин назад был опрос, надо проверить ответ и в противном случае отправить родителям
    if name == "Вова":
        go = "пошел"
        answer = "ответил"
    else:
        go = "пошла"
        answer = "ответила"
    info = pd.read_sql(f"SELECT answer, comment FROM user_family WHERE name ='{name}'", engine)
    if int(info.loc[0, "answer"]) == 0:
        text = f"{name} не {answer} на вопрос: \"Ты успеваешь на занятия?\""
    elif int(info.loc[0, "answer"]) == 1:  # Если 1, то это значит что ребенок ответил.
        bot.send_message(chat_id=943180118, text=f"{name} на вопрос: \"Ты успеваешь на занятия?\", {answer} \"Да\"")
        logging.info(f"{name} на вопрос: \"Ты успеваешь на занятия?\", {answer} \"Да\"")
    elif int(info.loc[0, "answer"]) == 2:  # Режим Я́беды-Коря́беды
        if info.loc[0, "comment"] != 'None' and info.loc[0, "comment"] is not None:
            text = f"{name} не {go} на занятия. На вопрос почему, {answer}: \"{info.loc[0, 'comment']}\""
        else:
            text = f"{name} не {go} на занятия. На вопрос почему, ответа не поступило."

    if text != '':
        logging.info(text)
        bot.send_message(chat_id=943180118, text=text)
        bot.send_message(chat_id=papa, text=text)
        bot.send_message(chat_id=mama, text=text)

def end(name,key):
    if name == "Вова":
        go = "пошел"
        answer = "ответил"
    else:
        go = "пошла"
        answer = "ответила"
        ########    Время после после окончания занятий, отправка опроса себенка    ########
    info = pd.read_sql(f"SELECT answer, comment, user_id FROM user_family WHERE name ='{name}'", engine)
    if key == 0:
        logging.info(f'{name}: НАЧАЛО.... Дай им знать когда будешь дома.')
        keyboard = [[InlineKeyboardButton('Я уже дома.', callback_data='home-' + str(name))],
                    [InlineKeyboardButton('Я не планирую пока идти домой.', callback_data='NO-' + str(name))]]
        bot.send_message(chat_id=int(info.loc[0, "user_id"]),
                         text='Родители беспокоются за тебя. Дай им знать когда ты уже будешь дома. 😊',
                         reply_markup=InlineKeyboardMarkup(keyboard))
        engine.execute(f"UPDATE user_family SET answer = 0, comment = 'None' WHERE name ='{name}'")
        logging.info(f'{name}:Родители беспокоются за тебя. Дай им знать когда будешь дома. end (key == 0)')
    ########    Время после после окончания занятий, каждый час срабатывает оповещение если ребенок не ответил    ########

    elif key == 1:
        if info.loc[0, "answer"] == 0:
            text = f"{name} не {answer} на вопрос: \"Ты дома?\""
        elif info.loc[0, "answer"] == 2:  # Режим Я́беды-Коря́беды
            if info.loc[0, "comment"] != 'None' and info.loc[0, "comment"] is not None:
                text = f"{name} не {go} домой. На вопрос почему, {answer}: \"{info.loc[0, 'comment']}\""
            else:
                text = f"{name} не {go} домой. На вопрос почему, ответа не поступило."
        if info.loc[0, "answer"] != 1:
            logging.info(str(text)+"  end (key == 1)")
            bot.send_message(chat_id=papa, text=text)
            bot.send_message(chat_id=mama, text=text)
        else:
            text = "info.loc[0, \"answer\"] = 1: key = 1 (ответ да)"
            logging.info(str(text))

def collect_info(name):
    credentials = pickle.load(open(f"{working_folder}calendar_tokens/token_{data_kids[name]}.pkl", "rb"))
    service = discovery.build("calendar", "v3", credentials=credentials)
    result = service.calendarList().list().execute()
    calendar_id = result['items'][0]['id']
    result = service.events().list(calendarId=calendar_id, timeZone="Europe/Moscow", singleEvents=True, orderBy="startTime", timeMin=datetime.now().strftime("%Y-%m-%dT00:00:00+03:00"), timeMax=datetime.now().strftime("%Y-%m-%dT23:59:59+03:00")).execute()
    nowDate = datetime.now().strftime("%Y-%m-%d")
    start = []
    end = []
    begin = 'None'
    zan = 'None'
    if result['items'] == []:
        bot.send_message(chat_id=943180118,text = name + ": В расписании ничего не заполнено на текущий день")
        logging.info(name + ": В расписании ничего не заполнено на текущий день")
        if name in time_begin_and_end:
            time_begin_and_end.pop(name)
    else:
        for i in range(len(result['items'])):
            if "start" in result['items'][i] and 'summary' in result['items'][i]:
                date_start = str(result['items'][i]['start']['dateTime'])
                date_end = str(result['items'][i]['end']['dateTime'])
                if date_start.split("T")[0] == nowDate:  # сверяем дату событий и выбираем только сегодня.
                    if date_start[:19].split("T")[1] >= "07:00:00":
                        start += [[date_start[:19].split("T")[1], i]]
                        end += [[date_end[:19].split("T")[1], i]]
            if start != []:
                begin = str(datetime.strptime(min(start)[0], "%H:%M:%S") - datetime.strptime("00:10:00", "%H:%M:%S"))  # +10 минут
                if int(begin.split(':')[0]) < 10:
                    begin = "0" + begin
                zan = str(result['items'][min(start)[1]]['summary'])
                if zan[len(zan) - 1:] == "а":
                    zan = zan[:len(zan) - 1] + "у"
                elif zan[len(zan) - 1:] == "я":
                    zan = zan[:len(zan) - 1] + "ю"
                # если в конце "а" меняем на "у", если "я" то на "ю"
    time_begin_and_end[name] = {
        'start': min(start),
        'end': max(end),
        'begin': begin,
        'zan': zan
    }
    #bot.send_message(chat_id=943180118,text = name + ": "+str(time_begin_and_end[name]))
    logging.info(name + ": "+str(time_begin_and_end[name]))

def nine_pm(name):
    info = pd.read_sql(f"SELECT mark, antimark, every_day, anti_every_day, sum_day_null, user_id FROM user_family WHERE name ='{name}'", engine)
    dislike_day = int(info.loc[0, "anti_every_day"])  # Принимаем целочисленную переменную
    like_day = int(info.loc[0, "every_day"])  # Принимаем целочисленную переменную
    ########    DSILIKE    ########
    if dislike_day != 0: #сравниваем переменную если она не равна нулю, то пошла жара
        if dislike_day > 20:
            dislike_day = int(str(dislike_day)[len(str(dislike_day)) - 1:])
        if dislike_day == 0 or (dislike_day >= 5 and dislike_day <= 20):
            dislike = "дизлайков"
        elif dislike_day >= 2 and dislike_day <= 4:
            dislike = "дизлайка"
        elif dislike_day == 1:
            dislike = "дизлайк"

        logging.info(f"{str(name)} 👎Получай от родителей {str(info.loc[0, 'anti_every_day'])} {str(dislike)}!👎")# для отчетности пишим в лог что отправили...
        #bot.send_message(chat_id=943180118, text=f"{str(name)} 👎Получай от родителей {str(info.loc[0, 'anti_every_day'])} {str(dislike)}!👎")# для отчетности пишим в лог что отправили...
        bot.send_message(chat_id=int(info.loc[0, "user_id"]),text=f"👎Получай от родителей {str(info.loc[0, 'anti_every_day'])} {dislike}!👎")
        engine.execute(f"UPDATE user_family SET anti_every_day = 0 WHERE name ='{str(name)}'")#обнуляем в БД значения
    ########    DISLIKE    ########
    ########    LIKE    ########
    if like_day != 0:# сравниваем переменную если она не равна нулю, то значит надо написать об этом ребенку
        if like_day > 20:
            like_day = int(str(like_day)[len(str(like_day)) - 1:])
        if like_day == 0 or (like_day >= 5 and like_day <= 20):
            like = "лайков"
        elif like_day >= 2 and like_day <= 4:
            like = "лайка"
        elif like_day == 1:
            like = "лайк"

        logging.info(f"{str(name)} 👍Получай от родителей {str(info.loc[0, 'every_day'])} {like}!👍")# для отчетности пишим в лог что отправили...
        #bot.send_message(chat_id=943180118, text=f"{str(name)} 👍Получай от родителей {str(info.loc[0, 'every_day'])} {like}!👍")# для отчетности пишим в лог что отправили...
        bot.send_message(chat_id=int(info.loc[0, "user_id"]),text=f"👍Получай от родителей {str(info.loc[0, 'every_day'])} {like}!👍")
        engine.execute(f"UPDATE user_family SET sum_day_null = 0, every_day = 0 WHERE name ='{name}'")#обнуляем в БД значения

    elif like_day == 0 and int(info.loc[0, "sum_day_null"]) == 3:# Если лайков за день 0 и на счетчике 3дней = 3, то отправляем смс ребенку
        logging.info(f"{str(name)} Лайков от родителей нет☹️. Завтра постарайся лучше.")# для отчетности пишим в лог что отправили...
        #bot.send_message(chat_id=943180118, text=f"{str(name)} Лайков от родителей нет☹️. Завтра постарайся лучше.")# для отчетности пишим в лог что отправили...
        bot.send_message(chat_id=int(info.loc[0, "user_id"]),text="Лайков от родителей нет ☹️. Завтра постарайся лучше.")
        engine.execute(f"UPDATE user_family SET sum_day_null = 0 WHERE name ='{name}'")

    elif like_day == 0 and int(info.loc[0, "sum_day_null"]) != 3: #Если лайков за день 0 и на счетчике 3дней не = 3, то прибавляем к счетчику +1
        engine.execute(f"UPDATE user_family SET sum_day_null = {int(info.loc[0, 'sum_day_null']) + 1} WHERE name ='{name}'")
    ########    LIKE    ########
    statistics_book(name, True, False)
    text = "Завтра у тебя в графике такие свободные промежутки времени:\n" +str(tomorrow(data_kids[name])) +"\n Расходуй время с пользой!🙂"
    #bot.send_message(chat_id=943180118,text=text)  # для отчетности пишим в лог что отправили...
    logging.info(text)  # для отчетности пишим в лог что отправили...
    bot.send_message(chat_id=int(info.loc[0, "user_id"]), text=text)

def statistics_book(name, flag, zero):
    book = pd.read_sql(f"SELECT * FROM books WHERE name ='{name}';",engine)
    summa = 0.0
    for num_book in range(len(book)):
        new_page = int(book.loc[num_book, "new_page"])
        old_page = int(book.loc[num_book, "old_page"])
        all_page = int(book.loc[num_book, "all_page"])
        every_day_page = int(book.loc[num_book, "every_day_page"])
        id_book = book.loc[num_book, "id"]
        if new_page != 0 and old_page <= new_page:
            norma = ((new_page - old_page) * 100) / every_day_page
            logging.info(f"{name}: norma = " + str(norma) + "%")
            summa += norma
            if zero:
                engine.execute(f"UPDATE books SET old_page = {new_page}, new_page = 0 WHERE id = {id_book};")
                engine.execute(f"UPDATE user_family SET dislike_book = 0 WHERE name ='{name}';")
                logging.info(f"{name} обнуление книги id = {id_book}")
            if all_page == new_page:
                engine.execute(f"UPDATE books SET name = 'Прочитано({name})' WHERE id = '{id_book}';")  #
    logging.info(f"{name}: summa = " + str(summa) + "%")
    if flag:
        if summa <= 99.99 and summa > 0.0:
            bot.send_message(chat_id=int(book.loc[0, "user_id"]), text=f"Сегодня прочитано недостаточно страниц, прочти еще немного. (Осталось {100 - int(summa + (0.5 if summa > 0 else -0.5))}%)")
            logging.info(f"{name} Сегодня прочитано недостаточно страниц, прочти еще немного. (Осталось {100 - int(summa + (0.5 if summa > 0 else -0.5))}%)")
        elif summa == 0.0:
            bot.send_message(chat_id=int(book.loc[0, "user_id"]), text="Надо почитать книгу! В противном случае будет дизлайк.")
            logging.info(f"{name} Надо почитать книгу! В противном случае будет дизлайк.")
    else:
        if summa <= 99.99 and summa > -1.0:
            dislike = antimark(name)
            text = f"Прочитанно {int(summa + (0.5 if summa > 0 else -0.5))}% от нормы за день. +{dislike}👎"
            logging.info(str(text))
            if name != "Константин":
                bot.send_message(chat_id=papa, text=name+": "+text)
                bot.send_message(chat_id=mama, text=name+": "+text)
            bot.send_message(chat_id=int(book.loc[0, "user_id"]), text=text)

def antimark(name_kid):
    info = pd.read_sql_query(f"SELECT mark, every_day, star, antimark, anti_every_day, poo, user_id,dislike_book FROM user_family WHERE name = '{name_kid}';",engine)
    dislike = int(info.loc[0, 'dislike_book'])
    if dislike != 0:
        dislike = dislike * 2
    else:
        dislike = 1
    new_antimark = dislike * 2
    antimark = int(info.loc[0, 'antimark']) + dislike
    anti_every_day = int(info.loc[0, 'anti_every_day']) + dislike
    poo = int(info.loc[0, 'poo'])
    mark = int(info.loc[0, 'mark'])
    every_day = int(info.loc[0, 'every_day'])
    star = int(info.loc[0, 'star'])
    if mark >= new_antimark:
        mark -= new_antimark
    elif star != 0:
        star -= 1
        mark = mark + 100 - new_antimark
    else:
        mark = 0
    if every_day >= new_antimark:
        every_day -= new_antimark
    else:
        every_day = 0
    if antimark >= 50:
        antimark -= 50
        poo += 1
    engine.execute(f"UPDATE user_family SET mark = {mark}, every_day = {every_day}, star = {star}, antimark = {antimark}, anti_every_day = {anti_every_day}, poo = {poo}, dislike_book = {dislike} WHERE name = '{name_kid}';")
    logging.info(f"{name_kid}: antimark = {dislike}")
    return dislike

def new_month(name):
    info = pd.read_sql(f"SELECT mark, antimark, star, poo, iq, brain, books_end FROM user_family WHERE name = '{name}'",engine)
    month = int(datetime.now().strftime('%m')) - 1
    year = int(datetime.now().strftime('%Y'))
    if month == 0:
        month = 12
        year -= 1
    engine.execute(f"INSERT INTO statistics(name, month, year, mark, antimark, star, poo, iq, brain, books_end) VALUES('{name}','{month}','{year}','{info.loc[0,'mark']}','{info.loc[0,'antimark']}','{info.loc[0,'star']}','{info.loc[0,'poo']}','{info.loc[0,'iq']}','{info.loc[0,'brain']}','{info.loc[0,'books_end']}');")
    engine.execute(f"UPDATE user_family SET star = 0, antimark = 0, anti_every_day = 0, poo = 0, brain = 0, books_end = 0  WHERE name = '{name}';")
    logging.info(f"new_month({name})")
def place():
    month = int(datetime.now().strftime('%m')) - 1
    year = int(datetime.now().strftime('%Y'))
    if month == 0:
        month = 12
        year -= 1
    info = pd.read_sql(f"SELECT name, mark, star, brain, iq FROM statistics WHERE month = '{month}' and year = '{year}';",engine)
    statistic = {}
    for i in range(len(info)):
        like = int(info.loc[i, "mark"])
        star = int(info.loc[i, "star"])
        brain = int(info.loc[i, "brain"])
        iq = int(info.loc[i, "iq"])
        result = (like+(star*100))+((brain*25)+(iq/2))
        statistic[info.loc[i, "name"]] = {
            "like": str(like),
            "result": result,
            "star": str(star),
            "place": 0
        }
    logging.info(f"Next function number place():")
    ########### Сбор информации ####################
    ########### Выявления победителя и раставления по местам ####################
    k = 0
    for j in range(len(info)):
        xyz = []
        for i in range(len(info)):
            if statistic[info.loc[i, "name"]]["place"] == 0:
                xyz += [[statistic[info.loc[i, "name"]]["result"], info.loc[i, "name"]]]
        k += 1
        statistic[max(xyz)[1]]["place"] = k
        engine.execute(f"UPDATE statistics SET place = {k} WHERE name = '{max(xyz)[1]}';")
        logging.info(f"place = {k}, name = '{max(xyz)[1]}'")
    ########### Выявления победителя и раставления по местам ####################

########### Функция для сбраса заданий в 7.00 и если они есть кидаем дизлайки ####################
def list_case_null(name_kid):
    info = pd.read_sql(f"SELECT id FROM list_case WHERE name = {name_kid}",engine)
    dislike = 0
    if len(info) != 0:
        for i in range(len(info)):
            engine.execute(f"UPDATE list_case SET name = '0' WHERE id = '{info.loc[i,'id']}';")
            dislike += 10
    if dislike != 0:
        info = pd.read_sql_query(f"SELECT mark, every_day, star, antimark, anti_every_day, poo, user_id FROM user_family WHERE name = '{name_kid}';",engine)
        new_antimark = dislike * 2
        antimark = int(info.loc[0, 'antimark']) + dislike
        anti_every_day = int(info.loc[0, 'anti_every_day']) + dislike
        poo = int(info.loc[0, 'poo'])
        mark = int(info.loc[0, 'mark'])
        every_day = int(info.loc[0, 'every_day'])
        star = int(info.loc[0, 'star'])
        if mark >= new_antimark:
            mark -= new_antimark
        elif star != 0:
            star -= 1
            mark = mark + 100 - new_antimark
        else:
            mark = 0
        if every_day >= new_antimark:
            every_day -= new_antimark
        else:
            every_day = 0
        if antimark >= 50:
            antimark -= 50
            poo += 1
        engine.execute(f"UPDATE user_family SET mark = {mark}, every_day = {every_day}, star = {star}, antimark = {antimark}, anti_every_day = {anti_every_day}, poo = {poo} WHERE name = '{name_kid}';")
        logging.info(f"{name_kid}: за невыполненное задание {dislike}👎.")
        bot.send_message(chat_id=int(info.loc[0, 'user_id']), text=f"Мне очень жаль, но за невыполненное задание, пришлось тебе поставить {dislike}👎.\nВозьми новое задание, выполняй и не забывай закрывать чтобы получать 👍!")
        bot.send_message(chat_id=papa,text=f"{name_kid}: за невыполненное задание {dislike}👎.")
        bot.send_message(chat_id=mama,text=f"{name_kid}: за невыполненное задание {dislike}👎.")

vkl = True
sleepTime = 1

while True:
    time = datetime.now().strftime('%H:%M:00')  # Время которое на сервере преобразованное в нужный нам вид
    day = datetime.now().strftime('%d') #какой сегодня день?
    minute = datetime.now().minute
    stopwatch1 = datetime.now()
    time1h = datetime.strptime(time, "%H:%M:%S") - datetime.strptime("01:00:00", "%H:%M:%S")  # -1 чвс
    time2h = datetime.strptime(time, "%H:%M:%S") - datetime.strptime("02:00:00", "%H:%M:%S")  # -1 чвс
    if minute%5 == 0:
        for name in kids:
            if name != "Константин":
                ########    Время после 04.00    ########
                if str(time) == "04:00:00" or vkl:
                    t = Thread(target=collect_info, args=(name,))  # Обновляем расписание
                    t.start()
                if vkl:
                    t.join()
                    #bot.send_message(chat_id=943180118, text=name+" - Обновляем расписание")
                    logging.info(name+" - Обновляем расписание")
                # try:
                #     if name in time_begin_and_end:
                #         if str(time_begin_and_end[name]['begin']) == str(time):
                #             Thread(target=begin,
                #                    args=(name, time_begin_and_end[name]['zan'],)).start()  # Обновляем расписание
                #         elif str(time_begin_and_end[name]['start'][0]) == str(time):
                #             Thread(target=start, args=(name,)).start()  # Обновляем расписание
                #         elif str(time_begin_and_end[name]['end'][0]) == str(time) or str(
                #                 time_begin_and_end[name]['end'][0]) == str(time1h) or str(
                #                 time_begin_and_end[name]['end'][0]) == str(time2h):
                #             key = 999
                #             if str(time_begin_and_end[name]['end'][0]) == str(time):
                #                 key = 0
                #             elif str(time_begin_and_end[name]['end'][0]) == str(time1h) or str(
                #                     time_begin_and_end[name]['end'][0]) == str(time2h):
                #                 key = 1
                #             Thread(target=end, args=(name, key,)).start()  # Обновляем расписание
                # except Exception as err:
                #     bot.send_message(chat_id=943180118, text=f"Error {str(time)} Begin-End ({name})\n{str(err)}")
                #     logging.info(f"Error {str(time)} Begin-End ({name})\n{str(err)}")
                if int(day) == 1 and str(time) == "07:05:00":
                    new_month(name)
                    bot.send_message(chat_id=943180118, text="new month " + name)
                    
        ########    Время после 07.00    ########
            if str(time) == "07:00:00":
                Thread(target=statistics_book,args=(name, False, True,)).start() # Проверяем,книги и при необходимости обнуляем или отправляем СМС
                Thread(target=list_case_null, args=(name, False, True,)).start()  # Проверяем остались ли задания на делях и при необходимости обнуляем, ставим дизлайки и отправляем СМС
            ########    Время после 21.00    ########
            if str(time) == "21:00:00":
                Thread(target=nine_pm,args=(name,)).start()# Мега проверка и оповещение
        vkl = False
        ########    Время после 07.00    ########
        if str(time) == "07:00:00":
            #bot.send_message(chat_id=943180118,text="7:00 сообщения отправил\n +str(time_begin_and_end) за 4:00 = \n"+str(time_begin_and_end))
            logging.info("7:00 сообщения отправил\n +str(time_begin_and_end) за 4:00 = \n"+str(time_begin_and_end))
        ########    Время после 21.00    ########
        if str(time) == "21:00:00":
            #bot.send_message(chat_id=943180118,text="21:00 сообщения отправил")
            logging.info("21:00 сообщения отправил")
        if int(day) == 1 and str(time) == "07:05:00":
            place()
            bot.send_message(chat_id=943180118, text="...new month, old place...")
    else:
        if sleepTime == 300:
            sleepTime = 60
            bot.send_message(chat_id=943180118, text="сбой по времени sleepTime == 300 ==> 60" + str(time))
            logging.info("сбой по времени sleepTime == 300 ==> 60" + str(time))
########    Отдел сна. Выравнивающий минуты и секунды чтобы в итоге спать по 5мин.    ########
    if sleepTime == 300:
        stopwatch2 = datetime.now()
        stopwatch = stopwatch2 - stopwatch1
        sleep(sleepTime - float(str(stopwatch).split(":")[2]))
    elif sleepTime == 60:
        if minute%5 == 0:
            sleepTime = 300
        stopwatch2 = datetime.now()
        stopwatch = stopwatch2 - stopwatch1
        sleep(sleepTime - float(str(stopwatch).split(":")[2]))

    else:
        sleep(sleepTime)
        if int(datetime.now().strftime("%S")) == 0:
            sleepTime = 60
        elif int(datetime.now().strftime("%S")) == 5:
            sleepTime = 5
        elif int(datetime.now().strftime("%S")) == 15:
            sleepTime = 15
        elif int(datetime.now().strftime("%S")) == 30:
            sleepTime = 30