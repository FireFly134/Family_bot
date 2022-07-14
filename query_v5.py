# coding=UTF-8
#
#

import logging
from datetime import datetime, timedelta
from time import sleep

import pandas as pd
import pickle
import telegram

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from apiclient import discovery
from sqlalchemy import create_engine
from threading import Thread

from work import TELEGRAM_TOKEN_TEST, ivea_family, papa, mama, kids, data_kids, working_folder
from free_time import tomorrow

bot = telegram.Bot(TELEGRAM_TOKEN_TEST)  # Коннект по токену

engine = create_engine(ivea_family)  # данные для соединия с сервером

time_begin_and_end = {}

logging.basicConfig(filename=working_folder + 'log/query_test_' + datetime.now().strftime('%d.%m.%Y') + '.log',
                    filemode='a',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%d.%m.%Y %H:%M:%S')


def add_dislike(name_kid, dislike, book=False):
    info = pd.read_sql_query(f"SELECT * FROM user_family WHERE name = '{name_kid}';", engine) # берем инфу о ребенке все что есть на него
    new_antimark = dislike * 2  # Т.к. у нас такой курс-валюты лайков и дизлайков всё приводим к уровню лайков.
    antimark = int(info.loc[0, 'antimark']) + dislike
    anti_every_day = int(info.loc[0, 'anti_every_day']) + dislike
    poo = int(info.loc[0, 'poo'])
    mark = int(info.loc[0, 'mark'])
    every_day = int(info.loc[0, 'every_day'])
    star = int(info.loc[0, 'star'])
    if mark <= new_antimark and star != 0:
        mark += (star * 100) - new_antimark
        if mark > 0:
            star = mark//100
            mark -= star * 100
        # star -= 1
        # mark = mark + 100 - new_antimark
    else:
        mark -= new_antimark
    if every_day >= new_antimark:
        every_day -= new_antimark
    else:
        every_day = 0
    if antimark >= 50:
        poo += antimark // 50
        antimark -= 50 * (antimark//50)
    if book:
        engine.execute("UPDATE user_family "
                       f"SET mark = {mark}, every_day = {every_day}, star = {star}, antimark = {antimark}, "
                       f"anti_every_day = 0, poo = {poo}, dislike_book = {dislike} " # anti_every_day = {anti_every_day}
                       f"WHERE name = '{name_kid}';")

    else:
        engine.execute(f"UPDATE user_family "
                       f"SET mark = '{mark}', every_day = '{every_day}', star = '{star}', antimark = '{antimark}', "
                       f"anti_every_day = '{anti_every_day}', poo = '{poo}' "
                       f"WHERE name = '{name_kid}';")
        bot.send_message(chat_id=943180118, text=f"add_dislike({name_kid}, {dislike})\nUPDATE user_family SET mark = '{mark}', every_day = '{every_day}', star = '{star}', antimark = '{antimark}', anti_every_day = '{anti_every_day}', poo = '{poo}', num_day_no_skill = '{int(info.loc[0, 'num_day_no_skill']) + 1}' WHERE name = '{name_kid}';")

def collect_info(name_kid):
    credentials = pickle.load(open(f"{working_folder}calendar_tokens/token_{data_kids[name_kid]}.pkl", "rb"))
    service = discovery.build("calendar", "v3", credentials=credentials, cache_discovery=False)
    result = service.calendarList().list().execute()
    calendar_id = result['items'][0]['id']
    result = service.events().list(calendarId=calendar_id, timeZone="Europe/Moscow", singleEvents=True,
                                   orderBy="startTime", timeMin=datetime.now().strftime("%Y-%m-%dT00:00:00+03:00"),
                                   timeMax=datetime.now().strftime("%Y-%m-%dT23:59:59+03:00")).execute()
    nowDate = datetime.now().strftime("%Y-%m-%d")
    start = []
    end = []
    begin = 'None'
    zan = 'None'
    if result['items'] == []:
        bot.send_message(chat_id=943180118, text=name_kid + ": В расписании ничего не заполнено на текущий день")
        logging.info(name_kid + ": В расписании ничего не заполнено на текущий день")
        if name_kid in time_begin_and_end:
            time_begin_and_end.pop(name_kid)
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
                begin = str(datetime.strptime(min(start)[0], "%H:%M:%S") - datetime.strptime("00:10:00",
                                                                                             "%H:%M:%S"))  # +10 минут
                if int(begin.split(':')[0]) < 10:
                    begin = "0" + begin
                zan = str(result['items'][min(start)[1]]['summary'])
                if zan[len(zan) - 1:] == "а":
                    zan = zan[:len(zan) - 1] + "у"
                elif zan[len(zan) - 1:] == "я":
                    zan = zan[:len(zan) - 1] + "ю"
                # если в конце "а" меняем на "у", если "я" то на "ю"
    time_begin_and_end[name_kid] = {
        'start': min(start),
        'end': max(end),
        'begin': begin,
        'zan': zan
    }
    # bot.send_message(chat_id=943180118,text = name + ": "+str(time_begin_and_end[name]))
    logging.info(name_kid + ": " + str(time_begin_and_end[name_kid]))

def statistics_book(name_kid, flag, zero):
    book = pd.read_sql(f"SELECT * FROM books WHERE name ='{name_kid}';", engine)
    summa = 0.0
    if len(book) != 0:  # if list not Null
        for num_book in range(len(book)):
            new_page = int(book.loc[num_book, "new_page"])  # Что прочитанно за сегодня
            old_page = int(book.loc[num_book, "old_page"])  # на какой странице остановились
            all_page = int(book.loc[num_book, "all_page"])  # сколько всего страниц
            every_day_page = int(
                book.loc[num_book, "every_day_page"])  # норма для прочтения, конкретной книги, за 1 день
            id_book = book.loc[num_book, "id"]  # id книги
            if new_page != 0 and old_page <= new_page:
                try:
                    norma = ((new_page - old_page) * 100) / every_day_page
                    logging.info(f"{name_kid}: id книги = {id_book} прочитано " + str(norma) + "%")
                    summa += norma
                    if zero:
                        engine.execute(f"UPDATE books SET old_page = {new_page}, new_page = 0 WHERE id = {id_book};")
                        engine.execute(f"UPDATE user_family SET dislike_book = 0 WHERE name ='{name_kid}';")
                        logging.info(f"{name_kid} обнуление книги id = {id_book}")
                    if all_page == new_page:
                        engine.execute(
                            f"UPDATE books SET name = 'Прочитано({name_kid})' WHERE id = '{id_book}';")  # Делаем для того чтобы она не отображалась
                except Exception as err:
                    logging.info(f"{name_kid}: id книги = {id_book} ошибка в расчетах")
                    logging.error(f"id книги = {id_book}\n{err}")
        logging.info(f"{name_kid}: сумма % от нормы чтения за день = " + str(summa) + "%")
        if flag:
            if summa <= 99.99 and summa > 0.0:
                bot.send_message(chat_id=int(book.loc[0, "user_id"]),
                                 text=f"Сегодня прочитано недостаточно страниц, прочти еще немного. (Осталось {100 - int(summa + (0.5 if summa > 0 else -0.5))}%)")
                logging.info(
                    f"{name_kid} Сегодня прочитано недостаточно страниц, прочти еще немного. (Осталось {100 - int(summa + (0.5 if summa > 0 else -0.5))}%)")
            elif summa == 0.0:
                bot.send_message(chat_id=int(book.loc[0, "user_id"]),
                                 text="Надо почитать книгу! В противном случае будет дизлайк.")
                logging.info(f"{name_kid} Надо почитать книгу! В противном случае будет дизлайк.")
        else:
            if summa <= 99.99 and summa > -1.0:
                info = pd.read_sql_query(f"SELECT * FROM user_family WHERE name = '{name_kid}';",
                                         engine)
                dislike = int(info.loc[0, 'dislike_book'])
                if dislike != 0:
                    dislike = dislike * 2
                else:
                    dislike = 1
                add_dislike(name_kid, dislike, book=True)
                text = f"Прочитанно {int(summa + (0.5 if summa > 0 else -0.5))}% от нормы за день. +{dislike}👎"
                logging.info(name_kid + ": " + text)
                if name_kid != "Константин":
                    bot.send_message(chat_id=papa, text=name_kid + ": " + text)
                    bot.send_message(chat_id=mama, text=name_kid + ": " + text)
                bot.send_message(chat_id=int(book.loc[0, "user_id"]), text=text)


def num_day_no_skill(name_kid):
    info = pd.read_sql_query(f"SELECT * FROM user_family WHERE name = '{name_kid}';", engine) # берем инфу о ребенке все что есть на него
    dislike = 0
    # Тут уже отдельное задание, проверяем как давно ребёнок не получал оценки за скил. где-то каждый день должно прибавляться.
    # Если есть определенное значение то прибавляется к дизлайкам нужное количество
    if int(info.loc[0, 'num_day_no_skill']) == 5:
        dislike = 10
    elif int(info.loc[0, 'num_day_no_skill']) == 10:
        dislike = 20
    elif int(info.loc[0, 'num_day_no_skill']) == 20:
        dislike = 30
    elif int(info.loc[0, 'num_day_no_skill']) == 30:
        dislike = 50
    # Если дизлайки есть то выполняем данную функцию
    if dislike != 0:
        add_dislike(name_kid, dislike, False)  # Функция которая прибавит дизлайки ребенку. передаем Имя, кол-во дизлайков, инфу из БД, и говорим что это не за книги(False)
        logging.info(f"{name_kid}: за {info.loc[0, 'num_day_no_skill']}дн. без оценок за 'skill' {dislike}.")
        bot.send_message(chat_id=int(info.loc[0, 'user_id']), text=f"Мне очень жаль, но за {info.loc[0, 'num_day_no_skill']}дн. без оценок за 'skill', пришлось тебе поставить {dislike}👎.")
        bot.send_message(chat_id=papa, text=f"{name_kid}: за {info.loc[0, 'num_day_no_skill']}дн. без оценок за 'skill' {dislike}👎.")
        bot.send_message(chat_id=mama, text=f"{name_kid}: за {info.loc[0, 'num_day_no_skill']}дн. без оценок за 'skill' {dislike}👎.")
        bot.send_message(chat_id=943180118, text=f"{name_kid}: за {info.loc[0, 'num_day_no_skill']}дн. без оценок за 'skill' {dislike}👎.")

def need_likes(name_kid):
    info = pd.read_sql(f"SELECT * FROM user_family WHERE name ='{name_kid}'", engine)
    dislike = int(info.loc[0, "antimark"])  # Принимаем целочисленную переменную с дизлайками
    like = int(info.loc[0, "mark"])  # Принимаем целочисленную переменную с лайками
    star = int(info.loc[0, "star"])  # Принимаем целочисленную переменную с звезд
    need_likes = int(tomorrow(data_kids[name_kid], True,-1))  # получаем нужное количество лайков для того чтобы не получить дизлайки
    likes = need_likes - int(info.loc[0, 'every_day']) # нужное колличество - набранное кол-во за день
    if likes > 0:  # Если в минусе, то хана)
        dislike += int(need_likes / 2)
        if like >= need_likes or (like < need_likes and star < 1):
            like -= need_likes
        else:
            like += 100 - need_likes
            star -= 1
        like_name = "лайков"
        if likes != 0:  # сравниваем переменную если она не равна нулю, то значит надо написать об этом ребенку
            duble_likes = likes
            if duble_likes > 20:
                duble_likes = int(str(likes)[len(str(likes)) - 1:])
            if duble_likes == 0 or (duble_likes >= 5 and duble_likes <= 20):
                like_name = "лайков"
            elif duble_likes >= 2 and duble_likes <= 4:
                like_name = "лайка"
            elif duble_likes == 1:
                like_name = "лайк"
        text = f"Вчера не было набрано {likes} {like_name} из необходимых {need_likes}."
        bot.send_message(chat_id=int(info.loc[0, "user_id"]), text=text)
        bot.send_message(chat_id=papa, text=f"{name_kid}: {text}")
        bot.send_message(chat_id=mama, text=f"{name_kid}: {text}")
        bot.send_message(chat_id=943180118,text=f"{name_kid}: {text}")
        logging.info(f"{name_kid}: {text}")
    if like > 0:
        sum_day_null = ', sum_day_null = 0'
    else:
        sum_day_null = ''
    engine.execute(f"UPDATE user_family SET mark ='{like}', antimark ='{dislike}', star = {star}, anti_every_day = 0{sum_day_null}, every_day = 0, num_day_no_skill = '{int(info.loc[0, 'num_day_no_skill']) + 1}' WHERE name ='{str(name_kid)}'")  # обнуляем в БД значения
    bot.send_message(chat_id=943180118, text=f"need_likes({name_kid})\nUPDATE user_family SET mark ='{like}', antimark ='{dislike}', star = {star}, anti_every_day = 0{sum_day_null}, every_day = 0, num_day_no_skill = '{int(info.loc[0, 'num_day_no_skill']) + 1}' WHERE name ='{str(name_kid)}'")

########### Функция для сбраса заданий в 7.00 и если они есть кидаем дизлайки ####################
def list_case_null(name_kid):
    info = pd.read_sql_query(f"SELECT * FROM user_family WHERE name = '{name_kid}';", engine) # берем инфу о ребенке все что есть на него
    engine.execute(f"INSERT INTO user_family_data_save "
                f"(name, mark, every_day, sum_day_null, antimark, anti_every_day, star, poo, iq, brain, dislike_book,books_end, num_day_no_skill, date_time) "
                f"VALUES('{name_kid}','{info.loc[0,'mark']}','{info.loc[0,'every_day']}','{info.loc[0,'sum_day_null']}','{info.loc[0,'antimark']}',"
                        f"'{info.loc[0,'anti_every_day']}','{info.loc[0,'star']}','{info.loc[0,'poo']}','{info.loc[0,'iq']}','{info.loc[0,'brain']}',"
                        f"'{info.loc[0,'dislike_book']}','{info.loc[0,'books_end']}','{info.loc[0,'num_day_no_skill']}','{datetime.now()}');")
    # ,'{info.loc[0,'']}'
    need_likes(name_kid)  # Переходим дальше с данным именем. Идет проверка на норму лайков в день и выполнение нормы.
    list_cases = pd.read_sql(f"SELECT id FROM list_cases WHERE name = '{name_kid}';",engine)  # Checking name kids in list  # проверяем еть ли в списке заданий имя ребенка(если список пуст то все ок)
    dislike = 0

    if len(list_cases) != 0:  # if there is a name in the list  # Если в списке заданий находится имя ребенка, то мы обнуляем выкатывая дизлайк
        for i in range(len(list_cases)):
            engine.execute(f"UPDATE list_cases SET name = '0', access_denied = '0' WHERE id = '{list_cases.loc[i, 'id']}';")  # delete a name from the list
            try:
                logging.info(f"name = '{name_kid}' не выполнено: {list_cases.loc[i, 'name_case']}")
            except Exception:
                logging.info(f"name = '{name_kid}' не выполнено: id = '{list_cases.loc[i, 'id']}'")
        dislike = 10  # and add 10 dislike


    #
    # Если дизлайки есть то выполняем данную функцию
    if dislike != 0:
        add_dislike(name_kid, dislike, False)  # Функция которая прибавит дизлайки ребенку. передаем Имя, кол-во дизлайков, инфу из БД, и говорим что это не за книги(False)
        logging.info(f"{name_kid}: за невыполненное задание {dislike}.")
        bot.send_message(chat_id=int(info.loc[0, 'user_id']), text=f"Мне очень жаль, но за невыполненное задание, пришлось тебе поставить {dislike}👎.\nВозьми новое задание, выполняй и не забывай закрывать чтобы получать 👍!")
        bot.send_message(chat_id=papa, text=f"{name_kid}: за невыполненное задание {dislike}👎.")
        bot.send_message(chat_id=mama, text=f"{name_kid}: за невыполненное задание {dislike}👎.")
        bot.send_message(chat_id=943180118, text=f"{name_kid}: за невыполненное задание {dislike}👎.")
    num_day_no_skill(name_kid)
    logging.info(" **** list_case_null(): выполнение завершено. ****")


def nine_pm(name_kid):
    info = pd.read_sql(f"SELECT* FROM user_family WHERE name ='{name_kid}'", engine)
    dislike_day = int(info.loc[0, "anti_every_day"])  # Принимаем целочисленную переменную
    like_day = int(info.loc[0, "every_day"])  # Принимаем целочисленную переменную
    ########    DSILIKE    ########
    if dislike_day != 0:  # сравниваем переменную если она не равна нулю, то пошла жара
        if dislike_day > 20:
            dislike_day = int(str(dislike_day)[len(str(dislike_day)) - 1:])
        if dislike_day == 0 or (dislike_day >= 5 and dislike_day <= 20):
            dislike = "дизлайков"
        elif dislike_day >= 2 and dislike_day <= 4:
            dislike = "дизлайка"
        elif dislike_day == 1:
            dislike = "дизлайк"

        logging.info(
            f"{str(name_kid)} 👎Получай от родителей {str(info.loc[0, 'anti_every_day'])} {str(dislike)}!👎")  # для отчетности пишим в лог что отправили...
        bot.send_message(chat_id=int(info.loc[0, "user_id"]),
                         text=f"👎Получай от родителей {str(info.loc[0, 'anti_every_day'])} {dislike}!👎")

    ########    DISLIKE    ########
    ########    LIKE    ########
    if like_day != 0:  # сравниваем переменную если она не равна нулю, то значит надо написать об этом ребенку
        if like_day > 20:
            like_day = int(str(like_day)[len(str(like_day)) - 1:])
        if like_day == 0 or (like_day >= 5 and like_day <= 20):
            like = "лайков"
        elif like_day >= 2 and like_day <= 4:
            like = "лайка"
        elif like_day == 1:
            like = "лайк"

        logging.info(
            f"{str(name_kid)} 👍Получай от родителей {str(info.loc[0, 'every_day'])} {like}!👍")  # для отчетности пишим в лог что отправили...
        bot.send_message(chat_id=int(info.loc[0, "user_id"]),
                         text=f"👍Получай от родителей {str(info.loc[0, 'every_day'])} {like}!👍")
    elif like_day == 0 and int(info.loc[
                                   0, "sum_day_null"]) == 3:  # Если лайков за день 0 и на счетчике 3дней = 3, то отправляем смс ребенку
        logging.info(
            f"{str(name_kid)} Лайков от родителей нет☹️. Завтра постарайся лучше.")  # для отчетности пишим в лог что отправили...
        bot.send_message(chat_id=int(info.loc[0, "user_id"]),
                         text="Лайков от родителей нет ☹️. Завтра постарайся лучше.")
        engine.execute(f"UPDATE user_family SET sum_day_null = 0 WHERE name ='{name_kid}'")

    elif like_day == 0 and int(info.loc[
                                   0, "sum_day_null"]) != 3:  # Если лайков за день 0 и на счетчике 3дней не = 3, то прибавляем к счетчику +1
        engine.execute(
            f"UPDATE user_family SET sum_day_null = {int(info.loc[0, 'sum_day_null']) + 1} WHERE name ='{name_kid}'")
    ########    LIKE    ########
    statistics_book(name_kid, True, False)
    text = f"Завтра у тебя в графике такие свободные промежутки времени:\n{tomorrow(data_kids[name_kid])}\n Расходуй время с пользой!🙂\n Твоя цель на завтра, набрать {tomorrow(data_kids[name_kid], True)}👍, выполняй задания чтобы достичь цели."
    logging.info(text)  # для отчетности пишим в лог что отправили...
    bot.send_message(chat_id=int(info.loc[0, "user_id"]), text=text)

def query_for_buy_products():
    categories = pd.read_sql(f"SELECT * FROM categories;", engine)
    info = pd.read_sql(f"SELECT name, user_id FROM user_family WHERE access in ('0','1');", engine)
    list_categories=[]
    keyboard = []
    for k in range(len(categories)):
        if categories.loc[k, 'frequency'] == categories.loc[k, 'num_day']:
            list_categories += [categories.loc[k,'name']]
            engine.execute(f"UPDATE categories SET num_day = 1 WHERE name ='{categories.loc[k,'name']}'")
        else:
            engine.execute(f"UPDATE categories SET num_day = {int(categories.loc[k, 'num_day'])+1} WHERE name ='{categories.loc[k, 'name']}'")
    for j in range(len(list_categories)):
        keyboard += [[InlineKeyboardButton(list_categories[j], callback_data='query_for_buy_products-'+str(list_categories[j]))]]
    if len(keyboard) > 1:
        sms = "Что-нибудь из данных категорий необходимо приобрести?"
    elif len(keyboard) == 0:
        return
    else:
        sms = "Что-нибудь из данной категории необходимо приобрести?"
    for i in range(len(info)):
        if info.loc[i,'name'] != 'Вова': #info.loc[i,'name'] != 'Константин' and 
            try:
                bot.send_message(chat_id=info.loc[i, 'user_id'], text=sms, reply_markup=InlineKeyboardMarkup(keyboard))
            except Exception:
                logging.error(f"не могу отправить опрос на продукты chat_id={info.loc[i, 'user_id']}")
def elections(): #  семейное голосование, кто будет проводить семейное мироприятие
    info = pd.read_sql(f"SELECT user_id FROM user_family WHERE access  in ('0','1');", engine)
    engine.execute(f"UPDATE user_family SET elections ='0';")
    keyboard = [[InlineKeyboardButton('Андрей', callback_data='elections-1')],
                [InlineKeyboardButton('Инна', callback_data='elections-2')],
                [InlineKeyboardButton('Амира', callback_data='elections-3')],
                [InlineKeyboardButton('Лиза', callback_data='elections-4')],
                [InlineKeyboardButton('Лейла', callback_data='elections-5')],
                [InlineKeyboardButton('Вова', callback_data='elections-6')]]
    sms = 'Кто хочет на следующей неделе провести объединяющее мероприятие для семьи?'
    for i in range(len(info)):
        bot.send_message(chat_id=info.loc[i, 'user_id'], text=sms, reply_markup=InlineKeyboardMarkup(keyboard))
def remind(): # напоминалка для Вовы, чтобы выпил таблетосы
    engine.execute("UPDATE user_family SET answer = 0, comment = 'None' WHERE user_id = '462169878';")
    sms = 'Напоминаю, нужно выпить таблетку.'
    bot.send_message(chat_id=462169878, text=sms, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Выпил', callback_data='YES-Вова')]]))
def check_remind():
    time = datetime.now().strftime('%H:%M:00')  # Время которое на сервере преобразованное в нужный нам вид
    time1h = datetime.strptime(time, "%H:%M:%S") - datetime.strptime("01:00:00", "%H:%M:%S")  # -1 час
    if '-1 day, ' in str(time1h):
        day = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        day = datetime.now().strftime('%Y-%m-%d')
    info = pd.read_sql(f"SELECT name FROM answer WHERE date > '{day} {str(time1h).replace('-1 day, ', '')}' and date < '{datetime.now().strftime('%Y-%m-%d %H:%M:00')}';", engine)
    print(f"SELECT name FROM answer WHERE date > '{day} {str(time1h).replace('-1 day, ', '')}' and date < '{datetime.now().strftime('%Y-%m-%d %H:%M:00')}';")
    if len(info) == 0 or (len(info) != 0 and info.loc[0,'name'] != 'Вова'):
        bot.send_message(chat_id=232749605, text="Вова не ответил, выпил ли он таблетку.")
##### Напоминалка 16.00 купи продукты ######
def remind_bay():
    date = datetime.now().strftime('%d.%m.%Y')
    # print(date)
    count = pd.read_sql_query(f"SELECT COUNT(*) FROM shopping_list WHERE order_date='{date}';", engine)
    # print(int(count.loc[0,'count']))
    if int(count.loc[0,'count']) > 0:
        # print(f"{date}\nСегодня были выбраны продукты для покупки: {count.loc[0,'count']} шт.\nПроверьте, может необходимо что-то докупить.")
        bot.send_message(chat_id=232749605, text=f"{date}\nСегодня было выбраны продукты для покупки: {count.len[0,'count']} шт.\nПроверьте, может необходимо что-то докупить.")
        bot.send_message(chat_id=943180118, text=f"{date}\nСегодня было выбраны продукты для покупки: {count.len[0,'count']} шт.\nПроверьте, может необходимо что-то докупить.")

vkl = True
sleepTime = 1

info = pd.read_sql_query(f"SELECT * FROM user_family WHERE name = 'Константин';",
                         engine)  # берем инфу о ребенке все что есть на него
engine.execute(f"INSERT INTO user_family_data_save "
               f"(name, mark, every_day, sum_day_null, antimark, anti_every_day, star, poo, iq, brain, dislike_book,books_end, num_day_no_skill, date_time) "
               f"VALUES('Константин','{info.loc[0, 'mark']}','{info.loc[0, 'every_day']}','{info.loc[0, 'sum_day_null']}','{info.loc[0, 'antimark']}',"
               f"'{info.loc[0, 'anti_every_day']}','{info.loc[0, 'star']}','{info.loc[0, 'poo']}','{info.loc[0, 'iq']}','{info.loc[0, 'brain']}',"
               f"'{info.loc[0, 'dislike_book']}','{info.loc[0, 'books_end']}','{info.loc[0, 'num_day_no_skill']}','{datetime.now()}');")

while True:
    time = datetime.now().strftime('%H:%M:00')  # Время которое на сервере преобразованное в нужный нам вид
    day = datetime.now().strftime('%d')  # какой сегодня день?
    minute = datetime.now().minute
    stopwatch1 = datetime.now()
    time1h = datetime.strptime(time, "%H:%M:%S") - datetime.strptime("01:00:00", "%H:%M:%S")  # -1 чвс
    time2h = datetime.strptime(time, "%H:%M:%S") - datetime.strptime("02:00:00", "%H:%M:%S")  # -2 чвс
    print(f"{str(time)} == '11:00:00' and {datetime.now().strftime('%w')} == '2':")
    if minute % 5 == 0:
        for name in kids:
            if name != "Константин":
                ########    Время после 04.00    ########
                if str(time) == "04:00:00" or vkl:
                    t = Thread(target=collect_info, args=(name,))  # Обновляем расписание
                    t.start()
                    logging.info(name + " - Обновляем расписание")
                if vkl:
                    t.join()
                    logging.info(name + " - Обновляем расписание")
            ########    Время после 07.00    ########
            if str(time) == "07:00:00":
                if name != "Константин":
                    Thread(target=list_case_null, args=(name,)).start()  # Проверяем остались ли задания на детях и при необходимости обнуляем, ставим дизлайки и отправляем СМС
                Thread(target=statistics_book, args=(name, False, True,)).start()  # Проверяем,книги и при необходимости обнуляем или отправляем СМС
            ########    Время после 21.00    ########
            """Вечером проверяем"""
            if str(time) == "21:00:00":
                Thread(target=nine_pm, args=(name,)).start()  # Мега проверка и оповещение
        vkl = False
        if str(time) == "07:10:00":
                Thread(target=query_for_buy_products, args=()).start()  # Проверяем остались ли задания на детях и при необходимости обнуляем, ставим дизлайки и отправляем СМС
        if str(time) == "19:00:00" and datetime.now().strftime('%w') == '0':
                Thread(target=elections, args=()).start()  # Каждое воскресенье прихоит СМС выборов.
        if str(time) == "09:00:00" or str(time) == "23:00:00":
            Thread(target=remind, args=()).start()  # Каждое вопрос для вовы, принял ли таблетосы.
        if str(time) == "10:00:00" or str(time) == "00:00:00":
            Thread(target=check_remind, args=()).start()  # чекаем, ответил ли Вова.
        if str(time) == "11:00:00" and datetime.now().strftime('%w') == '2': #Позвонить во вторник бабушке
            bot.send_message(chat_id=462169878, text="☎ Привет, позвони бабушке или дедушке.")
            bot.send_message(chat_id=2133224553, text="☎ Привет, позвони бабушке или дедушке.")
            # bot.send_message(chat_id=943180118, text="☎ Привет, позвони бабушке или дедушке.")
            logging.info("Сообщение: 'позвони бабушке или дедушке.' - отправленно!(вторник)")
        if str(time) == "11:00:00" and datetime.now().strftime('%w') == '3': #уточнить позвонили ли бабушке (среда)
            sms = "Привет, позвони бабушке или дедушке."
            bot.send_message(chat_id=462169878, text=sms,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("уже позвонил 📱",callback_data='call')]]))
            bot.send_message(chat_id=2133224553, text=sms,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("уже позвонила 📱",callback_data='call')]]))
            # bot.send_message(chat_id=943180118, text=sms,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("уже позвонил 📱",callback_data='call')]]))
            logging.info("Сообщение: 'позвони бабушке или дедушке. (с кнопкой)' - отправленно!(среда)")
        if str(time) == "11:00:00" and datetime.now().strftime('%w') == '4': #если не нажали подтверждение о звонке, написать Андрею.Д. (четверг)
            info = pd.read_sql_query(f"SELECT name FROM answer WHERE date > '{(datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')}' AND answer_kids = 'Да, позвонил(а)' ORDER BY date ASC;",engine)
            if len(info) == 0:
                bot.send_message(chat_id=papa, text="Никто не позвонил бабушке или дедушке.")
                # bot.send_message(chat_id=943180118, text="Никто не позвонил бабушке или дедушке.")
            elif len(info) == 1:
                if info.loc[0,"name"] == "Лиза":
                    sms = "Вова не позвонил бабушке или дедушке."
                else:
                    sms = "Лиза не позвонила бабушке или дедушке."
                bot.send_message(chat_id=papa, text=sms)
                # bot.send_message(chat_id=943180118, text=sms)
            logging.info(f"Проверка:{len(info)} - кол-во детей отметили что позвонили(четверг)")
        if str(time) == "16:00:00":
            Thread(target=remind_bay, args=()).start()  # проверяем добавились ли продукты, и напоминаем купить.
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
        if minute % 5 == 0:
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
