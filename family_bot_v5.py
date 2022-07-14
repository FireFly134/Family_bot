# coding=UTF-8
#
#
import pandas as pd
import logging
import time

from work import TELEGRAM_TOKEN_TEST, ivea_family, papa, mama, data_kids, working_folder, name_kids, kids
from flow_my import InstalledAppFlow
import pickle

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from sqlalchemy import create_engine
from threading import Thread
from datetime import datetime, timedelta

from additional_menu.triger import handle_text as triger, eat, products, categories, frequency, dish
from additional_menu.parents import handle_text as parents
from additional_menu.children import handle_text as children

# logging.basicConfig(filename=working_folder + 'bot_v3.log',
#                     filemode='a',
#                     level=logging.INFO,
#                     format='%(asctime)s %(process)d-%(levelname)s %(message)s',
#                     datefmt='%d-%b-%y %H:%M:%S')

engine = create_engine(ivea_family)  # данные для соединия с сервером

updater = Updater(token=TELEGRAM_TOKEN_TEST, use_context=True)  # потключаемся к управлению ботом по токену

dispatcher = updater.dispatcher

user_triger = {}

data = {
    232749605: "Андрей",
    903477454: "Инна",
    943180118: "Костя",
    462169878: "Вова",
    'name_institut': ['Технологический университет', 'Информационно-технологический', 'Финансовый университет', 'Высшая школа экономики','МГТУ Станкин','НИЯУ МИФИ'],
    'link_institut': ['https://t.me/+eq5FJ2phgpUwYzI6', 'https://t.me/+CDFlnO4DGhliODBi', 'https://t.me/+4OzrVgjOEBUwMTYy', 'https://t.me/+GgnRSXCMUoMyYWMy','https://stankin.ru/','https://www.mephi.ru/']
}

def start(update: Update, context: CallbackContext):
    search_result = engine.execute(f"SELECT name,access FROM user_family WHERE user_id = '{str(update.effective_chat.id)}';").fetchall()
    if len(search_result) != 0:
        if str(search_result[0][1]) == "1" or str(search_result[0][1]) == "2":#update.effective_chat.id == 232749605 or update.effective_chat.id == 943180118:
            sms = f"Здравствуйте, {str(search_result[0][0])}."
        else:
            sms = f'Привет, {str(search_result[0][0])}'
        user(update, context,sms)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Я Вас не знаю. Давайте знакомиться, как Вас зовут?")
        user_triger[update.effective_chat.id] = {
            "triger":"reg"
        }

def token_download(update, context, num = 0):
    scopes = ['https://www.googleapis.com/auth/calendar']
    flow = InstalledAppFlow.from_client_secrets_file(f"{working_folder}calendar_tokens/client_secret_{data_kids[kids[num]]}.json", scopes=scopes)
    link = flow.run_console_url()
    context.bot.send_message(chat_id=943180118, text=str(kids[num]))
    context.bot.send_message(chat_id=943180118, text=str(link))
    user_triger[943180118] = {
        "triger": "token",
        "num": num,
        "flow": flow
    }


def user(update, context,sms):
    search_result = engine.execute(f"SELECT name,access FROM user_family WHERE user_id = '{str(update.effective_chat.id)}';").fetchall()
    if len(search_result) != 0:
        if update.effective_chat.id in user_triger:
            user_triger.pop(update.effective_chat.id)
        if str(search_result[0][1]) == "1":#update.effective_chat.id == 232749605 or update.effective_chat.id == 943180118:
            reply_keyboard = [['Амира','Лиза','Лейла','Вова'], ['Список дел...', 'Институт'],['Хотят похвалу','Оценить','Статистика']]
        elif str(search_result[0][1]) == "2":#update.effective_chat.id == 232749605 or update.effective_chat.id == 943180118:
            reply_keyboard = [['Амира','Лиза','Лейла','Вова'], ['Хотят похвалу', 'Статистика']]
        else:
            reply_keyboard = [['Книги'],['Хочу похвалу','Skill','мой список дел'],['Статистика']]
        if update.effective_chat.id == 462169878:
            reply_keyboard += [['Проблемы', 'Институт','Еда']]
        else:
            if str(search_result[0][1]) != "2":
                reply_keyboard += [['Сообщить о проблеме','Еда']]
        context.bot.send_message(chat_id=update.effective_chat.id, text=sms, reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=False))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Я Вас не знаю. Давайте знакомиться, как Вас зовут?")
        user_triger[update.effective_chat.id] = {
            "triger":"reg"
        }
# def mega_msg(update, context):
#     search_result = pd.read_sql_query(f"SELECT name,access,user_id FROM user_family WHERE access = 0;", engine)
#     for i in range(len(search_result)):
#         if str(search_result.loc[i, 'access']) == "0":  # update.effective_chat.id == 232749605 or update.effective_chat.id == 943180118:
#             sms = f'Привет, {str(search_result.loc[i, "name"])}, новые правила!\nЗа отсутствие новых скилов внедряется система штрафов:\nесли нет новых скилов, то...\nна 5й день = 10👎\nна 10й день = 20👎\nна 20й день = 30👎\nна 30й день = 50👎\nТы уже можешь заметить отсутствие большого количества лайков по этой причине.'
#             try:
#                 context.bot.send_message(chat_id=int(search_result.loc[i, 'user_id']), text=sms)
#                 logging.info(f'{str(search_result.loc[i, "name"])} - Сообщение получено.')
#             except Exception:
#                 logging.info(f'{str(search_result.loc[i, "name"])} - Сообщение не получено.')
def mega_msg(update, context):
    user_triger[update.effective_chat.id] = {
        "triger": "mega_msg",
    }
    context.bot.send_message(chat_id=update.effective_chat.id, text="Напишите что нужно передать!")

def button(update: Update, context: CallbackContext) -> None:  # реагирует на нажатие кнопок.
    query = update.callback_query
    query.answer()
    if 'YES' in query.data:
        engine.execute(f"INSERT INTO answer(date, name, answer_kids) VALUES('{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}','{str(query.data.split('-')[1])}','Да');")
        engine.execute("UPDATE user_family SET answer = 1, comment = 'None' WHERE user_id = '" + str(update.effective_chat.id) +"';")
        context.bot.send_message(chat_id=papa, text=str(query.data.split('-')[1]) + " таблетку подтвердил.")#"( Ответ ДА)")
        query.edit_message_text("Отлично!😊")
    elif 'NO' in query.data:
        engine.execute(f"INSERT INTO answer(date, name, answer_kids) VALUES('{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}','{str(query.data.split('-')[1])}','Нет');")
        engine.execute("UPDATE user_family SET answer = 2, comment = 'None' WHERE user_id = '" + str(update.effective_chat.id) + "';")
        context.bot.send_message(chat_id=papa, text=str(query.data.split('-')[1]) + " (Ответ НЕТ)")
        user_triger[update.effective_chat.id] = {
            "triger": "comment",
            "name": str(query.data.split('-')[1])
        }
        query.edit_message_text("Пожалуйста напиши причину")
        logging.info(str(query.data.split('-')[1]) + " (Ответ Нет) Пожалуйста напиши причину")
        Thread(target=Timer, args=(update, context, 600)).start()
    elif 'antimark' in query.data:
        name_kid = str(query.data.split('-')[1])
        info = pd.read_sql_query(f"SELECT mark, every_day, star, antimark, anti_every_day, poo, user_id FROM user_family WHERE name = '{name_kid}';", engine)
        recipient = pd.read_sql_query(f"SELECT name, user_id FROM user_family WHERE access = '2';", engine)
        new_antimark = int(query.data.split('-')[2]) * 2
        antimark = int(info.loc[0,'antimark'])+int(query.data.split('-')[2])
        anti_every_day = int(info.loc[0,'anti_every_day'])+int(query.data.split('-')[2])
        poo = int(info.loc[0,'poo'])
        mark = int(info.loc[0, 'mark'])
        every_day = int(info.loc[0, 'every_day'])
        star = int(info.loc[0,'star'])
        if mark <= new_antimark and star != 0:
            mark += (star * 100) - new_antimark
            if mark > 0:
                star = mark // 100
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
            antimark -= 50 * (antimark // 50)
        engine.execute(f"UPDATE user_family SET mark = {mark}, every_day = {every_day}, star = {star},antimark = {antimark}, anti_every_day = {anti_every_day}, poo = {poo} WHERE name = '{name_kid}';")
        update.callback_query.message.delete()
        user(update,context,query.message.text + " " + str(query.data.split('-')[2]) + "👎")
        kto = ''
        if papa == update.effective_chat.id:
            kto = "папы"
        elif mama == update.effective_chat.id:
            kto = "мамы"
        if poo == 0:
            sms = f"+{str(query.data.split('-')[2])}👎 от {kto}\n Всего дизлайков = {str(antimark)}"
        else:
            sms = f"+{str(query.data.split('-')[2])}👎 от {kto}\n Всего дизлайков = {str(antimark)}\n Всего 💩 = {str(poo)}"
        logging.info(str(name_kid) + " - " + sms)
        context.bot.send_message(chat_id=int(info.loc[0, 'user_id']), text=sms)
        for i in range(len(recipient)):
            try:
                context.bot.send_message(chat_id=int(recipient.loc[i, 'user_id']), text=str(name_kid) + " - " + sms)
            except Exception:
                logging.error(f"{recipient.loc[i, 'name']} не смог отправить смс 'об выставленной оценки.'")

    elif 'mark' in query.data:
        name_kid = str(query.data.split('-')[1])
        info = pd.read_sql_query(f"SELECT mark, every_day, star, user_id FROM user_family WHERE name = '{name_kid}';", engine)
        recipient = pd.read_sql_query(f"SELECT name, user_id FROM user_family WHERE access = '2';", engine)
        mark = int(info.loc[0,'mark'])+int(query.data.split('-')[2])
        every_day = int(info.loc[0,'every_day'])+int(query.data.split('-')[2])
        star = int(info.loc[0,'star'])
        if mark >= 100:
            mark -= 100
            star += 1
        engine.execute(f"UPDATE user_family SET mark = {mark}, every_day = {every_day}, star = {star} WHERE name = '{name_kid}';")
        update.callback_query.message.delete()
        user(update,context,query.message.text + " " + str(query.data.split('-')[2]) + "👍")
        kto = ''
        if papa == update.effective_chat.id:
            kto = "папы"
        elif mama == update.effective_chat.id:
            kto = "мамы"
        if star == 0:
            sms = f"+{str(query.data.split('-')[2])}👍 от {kto}\n Всего лайков = {str(mark)}"
        else:
            sms = f"+{str(query.data.split('-')[2])}👍 от {kto}\n Всего лайков = {str(mark)}\n Всего звёзд⭐ = {str(star)}"
        logging.info(str(name_kid) + " - " + sms)
        context.bot.send_message(chat_id=int(info.loc[0,'user_id']),text=sms)
        for i in range(len(recipient)):
            try:
                context.bot.send_message(chat_id=int(recipient.loc[i, 'user_id']), text=str(name_kid) + " - " + sms)
            except Exception:
                logging.error(f"{recipient.loc[i, 'name']} не смог отправить смс 'об выставленной оценки.'")

    elif 'IQ' in query.data:
        name_kid = str(query.data.split('-')[1])
        info = pd.read_sql_query(f"SELECT iq, brain, user_id FROM user_family WHERE name = '{name_kid}';", engine)
        recipient = pd.read_sql_query(f"SELECT name, user_id FROM user_family WHERE access = '2';", engine)
        iq = int(info.loc[0,'iq'])+int(query.data.split('-')[2])
        brain = int(info.loc[0,'brain'])
        if iq >= 50:
            iq -= 50
            brain += 1
        engine.execute(f"UPDATE user_family SET iq = {iq}, brain = {brain}, num_day_no_skill = 0 WHERE name = '{name_kid}';")
        update.callback_query.message.delete()
        user(update,context,query.message.text + " " + str(query.data.split('-')[2]) + "💡")
        kto = ''
        if papa == update.effective_chat.id:
            kto = "папы"
        elif mama == update.effective_chat.id:
            kto = "мамы"
        if brain == 0:
            sms = f"+{str(query.data.split('-')[2])}💡 от {kto}\n Всего IQ 💡 = {str(iq)}"
        else:
            sms = f"+{str(query.data.split('-')[2])}💡 от {kto}\n Всего IQ 💡 = {str(iq)}\n Всего 🧠 = {str(brain)}"
        logging.info(str(name_kid) + " - " + sms)
        context.bot.send_message(chat_id=int(info.loc[0,'user_id']),text=sms)
        for i in range(len(recipient)):
            try:
                context.bot.send_message(chat_id=int(recipient.loc[i, 'user_id']), text=str(name_kid) + " - " + sms)
            except Exception:
                logging.error(f"{recipient.loc[i, 'name']} не смог отправить смс 'об выставленной оценки.'")

    elif 'home' in query.data:
        engine.execute("UPDATE user_family SET answer = 1, comment = 'None' WHERE user_id = '" + str(update.effective_chat.id) +"';")
        logging.info(str(query.data.split('-')[1]) +"Дома, Отлично!😊")
        query.edit_message_text("Отлично!😊")
        context.bot.send_message(chat_id=papa, text=str(query.data.split('-')[1]) + ", уже дома.")
        context.bot.send_message(chat_id=mama, text=str(query.data.split('-')[1]) + ", уже дома.")
    elif 'add_book' in query.data:
        book_id = query.data.split('-')[1]
        user_triger[update.effective_chat.id] = {
            "triger": "norma_for_new_book",
            "book_id": book_id
        }
        update.callback_query.message.delete()
        context.bot.send_message(chat_id=papa, text=query.message.text +"\n\nВведите суточную норму для этой книги.")
    elif 'book' in query.data:
        if query.data.split('-')[1] != "0":
            info = pd.read_sql_query(f"SELECT id, name, book_name, all_page, every_day_page, old_page, new_page FROM books WHERE id = {query.data.split('-')[1]};", engine)
            id = info.loc[0, "id"]
            name = info.loc[0, 'name']
            old_page = int(info.loc[0, 'old_page'])
            book = info.loc[0, "book_name"]
            every_day_page = info.loc[0, "every_day_page"]
            all_page = info.loc[0, "all_page"]
            books(update, context, id, name, old_page, book, every_day_page, all_page)
        else:
            user_triger[update.effective_chat.id] = {
                "triger": "add_book",
                "name_book": "None",
                "name_writer": "None",
                "all_page": "None"
            }
            reply_keyboard = [['Отмена']]
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Хорошо, давай начнем с названия книги. Как называется книга?",
                                     reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                      one_time_keyboard=False))
            logging.info("Going add_book()")
        update.callback_query.message.delete()
    elif 'no_problem' in query.data:
        id_p = str(query.data.split('-')[1])
        engine.execute(f"UPDATE msg_list_work SET make = 1 WHERE id = '{id_p}';")
        query.edit_message_text("Отлично, минус одна проблема...")
        logging.info("Отлично, минус одна проблема...")
        info = pd.read_sql_query(f"SELECT user_id, msg_text FROM msg_list_work WHERE id = '{id_p}';",engine)
        context.bot.send_message(chat_id=info.loc[0, 'user_id'], text=f"Проблема решена:\n{str(info.loc[0, 'msg_text'])}")
        logging.info(f"Проблема решена:\n{str(info.loc[0, 'msg_text'])}")
    elif 'case' in query.data:
        id = int(query.data.split('-')[1])
        user_id = int(query.data.split('-')[2])
        info = pd.read_sql_query(f"SELECT name_case, repeated_day, repeated_date, num_of_likes, antiduble FROM list_cases WHERE id = '{id}';", engine)
        if info.loc[0,'antiduble'] == 0:
            if str(query.data.split('-')[3]) == "yes":
                repeated_date = datetime.now() + timedelta(days=+int((info.loc[0,"repeated_day"])))
                engine.execute(f"UPDATE list_cases SET repeated_date = '{repeated_date.strftime('%Y-%m-%d 00:00:00')}', name = '0', antiduble = '1', access_denied = 0 WHERE id = '{id}';")
                info_mark = pd.read_sql_query(f"SELECT mark, every_day, star FROM user_family WHERE user_id = '{user_id}';", engine)
                mark = int(info_mark.loc[0, 'mark']) + int(info.loc[0,'num_of_likes'])
                every_day = int(info_mark.loc[0, 'every_day']) + int(info.loc[0,'num_of_likes'])
                star = int(info_mark.loc[0, 'star'])
                if mark >= 100:
                    mark -= 100
                    star += 1
                engine.execute(f"UPDATE user_family SET mark = {mark}, every_day = {every_day}, star = {star} WHERE user_id = '{user_id}';")

                sms = f"Выполнение задачи \"{info.loc[0,'name_case']}\" подтверждено! +{info.loc[0,'num_of_likes']}👍"
            else:
                sms = f"Выполнение задачи \"{info.loc[0,'name_case']}\" не подтверждено."
            context.bot.send_message(chat_id=mama, text=str(name_kids[user_id])+":\n"+sms)
            context.bot.send_message(chat_id=papa, text=str(name_kids[user_id])+":\n"+sms)
            context.bot.send_message(chat_id=user_id, text=sms)
            logging.info(f"{str(name_kids[user_id])}:\nВыполнение задачи \"{info.loc[0,'name_case']}\" подтверждено! +{info.loc[0,'num_of_likes']}")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Данная задача уже закрыта.")
        update.callback_query.message.delete()
    elif 'query_for_buy_products' in query.data:
        categories = query.data.split('-')[1]
        products_pd = pd.read_sql_query(f"SELECT name, link,id FROM products WHERE categories = '{categories}';", engine)
        keyboard = []
        if len(products_pd) != 0:
            text = ''
            for i in range(len(products_pd)):
                text += f"{i + 1}) {products_pd.loc[i, 'name']} ({products_pd.loc[i, 'link']})\n"
                keyboard += [[InlineKeyboardButton(f"{i + 1}) {products_pd.loc[i, 'name']}", callback_data='query_for_buy_next-'+str(products_pd.loc[i, 'id']))]]
            context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=InlineKeyboardMarkup(keyboard))
            user_triger[update.effective_chat.id]={
                'triger': 'None',
                'categories': categories,
                'products_name': "None"
            }
    elif 'query_for_buy_next' in query.data:
        id = query.data.split('-')[1]
        products_pd = pd.read_sql_query(f"SELECT name FROM products WHERE id = '{id}';",engine)
        user_triger[update.effective_chat.id]['triger'] = 'query_for_buy_next'
        user_triger[update.effective_chat.id]['products_name'] = products_pd.loc[0, 'name']
        query.edit_message_text(f"Введите количество шт. для закупки \"{products_pd.loc[0,'name']}\".")
        context.bot.send_message(chat_id=update.effective_chat.id, text="Или нажмите на кнопку \"Отменить ввод\"",reply_markup=ReplyKeyboardMarkup([['Отменить ввод']], resize_keyboard=True,
                                                              one_time_keyboard=False))
        # context.bot.send_message(chat_id=update.effective_chat.id, text="Введите количество шт. для закупки.")
    elif 'dish_choice_categories' in query.data:
        categories_name = query.data.split('-')[1]
        if categories_name != 'back': # Если в категории слово back, то это значит что мы хотим вернуться назад к категориям
            products_pd = pd.read_sql_query(f"SELECT id, name FROM products WHERE categories = '{categories_name}';",engine)
            keyboard = []
            for j in range(len(products_pd)):
                keyboard += [[InlineKeyboardButton(products_pd.loc[j, 'name'], callback_data='dish_choice_products-' + str(products_pd.loc[j, 'id']))]]
            keyboard += [[InlineKeyboardButton("Вернуться к категориям", callback_data='dish_choice_categories-back')]]
            sms = "Что из данных продуктов необходимо приобрести для приготовления данного блюда?"
            query.edit_message_text(sms, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            categories = pd.read_sql(f"SELECT * FROM categories;", engine)
            keyboard = []
            for j in range(len(categories)):
                keyboard += [[InlineKeyboardButton(categories.loc[j, 'name'],
                                                   callback_data='dish_choice_categories-' + str(
                                                       categories.loc[j, 'name']))]]
            keyboard += [[InlineKeyboardButton("Сохранить", callback_data='dish_saved-begin')]]
            sms = "Что из данных категорий необходимо приобрести для приготовления данного блюда?"
            query.edit_message_text(sms, reply_markup=InlineKeyboardMarkup(keyboard))
    elif 'dish_choice_products' in query.data:
        id_products = query.data.split('-')[1]
        user_triger[update.effective_chat.id]['list_products'] += [id_products]
        context.bot.send_message(chat_id=update.effective_chat.id, text='В список добавил. Вернитесь в раздел категорий и нажмите сохранить или выберите еще продукт.')
    elif 'dish_saved' in query.data: # Button "save" сохраняем новое блюдо
        step = query.data.split('-')[1]
        list_name_product = ''
        for id_product in user_triger[update.effective_chat.id]['list_products']:
            info = pd.read_sql(f"SELECT name FROM products WHERE id = '{id_product}';",engine)
            list_name_product += f"• {str(info.loc[0, 'name'])}\n"
        sms = f"Название блюда: {user_triger[update.effective_chat.id]['name']}\n" \
              f"Необходимые продукты для приготовления:\n{list_name_product}\n" \
              f"Так же для приготовления необходимо {user_triger[update.effective_chat.id]['num_need_people']} чел. и займет это по времени {user_triger[update.effective_chat.id]['cooking_time']} "
        if step == 'begin':
            keyboard = [[InlineKeyboardButton("Все верно, сохранить.", callback_data='dish_saved-end')]]
            query.edit_message_text(sms, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            update.callback_query.message.delete()
            if update.effective_chat.id in user_triger:
                list_product = str(user_triger[update.effective_chat.id]['list_products']).replace('\'', '').replace('[', '').replace(']', '').replace(' ', '')
                engine.execute(f"INSERT INTO dish(name, list_product, cooking_time, num_need_people) VALUES('{str(user_triger[update.effective_chat.id]['name']).replace('%', '%%')}','{list_product}', '{user_triger[update.effective_chat.id]['cooking_time']}', '{user_triger[update.effective_chat.id]['num_need_people']}');")
                info2 = pd.read_sql(f"SELECT id FROM dish WHERE name = '{user_triger[update.effective_chat.id]['name']}';", engine)
                keyboard = [[InlineKeyboardButton("Установить кол-во лайков.", callback_data='dish_like-'+str(info2.loc[0,'id']))]]
                context.bot.send_message(chat_id=papa, text=sms, reply_markup=InlineKeyboardMarkup(keyboard))
                eat(update, context, user_triger)
    elif 'dish_add' in query.data: # Добавление продуктов для блюда в корзину
        id = query.data.split('-')[1]
        dish = pd.read_sql(f"SELECT * FROM dish WHERE id = '{id}';", engine)
        list_products = str(dish.loc[0,'list_product']).split(',')
        user_name = pd.read_sql(f"SELECT name FROM user_family WHERE user_id = '{update.effective_chat.id}';", engine)
        for i in list_products:
            info = pd.read_sql(f"SELECT * FROM products WHERE id = '{i}';", engine)
            shopping_pd = pd.read_sql(f"SELECT * FROM shopping_list WHERE categories = '{info.loc[0,'categories']}' and products = '{str(info.loc[0,'name']).replace('%', '%%')}';",engine)
            if len(shopping_pd) == 0:
                and_name = ''
                quantity = 1
            else:
                and_name = f" и {shopping_pd.loc[0, 'name']}"
                quantity = int(shopping_pd.loc[0, 'quantity']) + 1
            engine.execute(f"INSERT INTO shopping_list(categories, products, quantity, name, order_date) "
                           f"VALUES('{info.loc[0,'categories']}',"
                           f"'{str(info.loc[0,'name']).replace('%', '%%')}',"
                           f"'{quantity}','для блюда \"{dish.loc[0, 'name']}\" - {user_name.loc[0, 'name']}{and_name}',"
                           f"'{str(datetime.now().strftime('%d.%m.%Y'))}');")
        update.callback_query.message.delete()
        context.bot.send_message(chat_id=update.effective_chat.id, text="Продукты для данного блюда успешно добавлены.")
    elif 'dish_like' in query.data: #сохраняем лайки которые будем отдавать за приготовления данного блюда
        update.callback_query.message.delete()
        context.bot.send_message(chat_id=update.effective_chat.id, text="Введите количество лайков которое должно начисляться при выполнении данного блюда.")
        user_triger[update.effective_chat.id] = {
            'triger': 'dish_like',
            'id': query.data.split('-')[1]
        }
    elif 'elections_upgrade' in query.data:
        info2 = pd.read_sql(f"SELECT * FROM user_family ORDER BY elections DESC;", engine)
        sms = ''
        for i in range(len(info2)):
            if info2.loc[i, 'name'] != 'Константин':
                space = " " * ((10-len(info2.loc[i, 'name']))*2)
                sms += f"{info2.loc[i, 'name']}{space}{info2.loc[i, 'elections']}❤️\n"
        keyboard = [[InlineKeyboardButton("Обновить результаты голосования.", callback_data='elections_upgrade')]]
        query.edit_message_text(sms, reply_markup=InlineKeyboardMarkup(keyboard))
    elif 'elections' in query.data:
        id = query.data.split('-')[1]
        info = pd.read_sql(f"SELECT elections FROM user_family WHERE id = {id};", engine)
        engine.execute(f"UPDATE user_family SET elections ='{int(info.loc[0,'elections']) + 1}' WHERE id = '{id}';")  #
        engine.execute(f"UPDATE user_family SET elections_date ='{datetime.now()}' WHERE user_id = '{update.effective_chat.id}';")
        info2 = pd.read_sql(f"SELECT * FROM user_family ORDER BY elections DESC;", engine)
        sms = ''
        for i in range(len(info2)):
            if info2.loc[i,'name'] != 'Константин':
                space = " " * ((10 - len(info2.loc[i, 'name'])) * 2)
                sms += f"{info2.loc[i,'name']}{space}{info2.loc[i, 'elections']}❤️\n"
        keyboard = [[InlineKeyboardButton("Обновить результаты голосования.", callback_data='elections_upgrade')]]
        query.edit_message_text(sms, reply_markup=InlineKeyboardMarkup(keyboard))
        sum_elections = info2['elections'].sum()
        if sum_elections >= 6:
            for i in range(len(info2)):
                context.bot.send_message(chat_id=info2.loc[i,'user_id'],text=f"Голосование завершено.\nМы решили, что {info2.loc[0,'name']}, отличный кандидат для данной задачи.")
        else:
            list_elections = ''
            for j in range(len(info2)):
                if str(info2.loc[j,'elections_date']).split(' ')[0] == datetime.now().strftime("%Y-%m-%d"):
                    list_elections += f"{info2.loc[j, 'name']}, "
            for i in range(len(info2)):
                if list_elections != '':
                    context.bot.send_message(chat_id=info2.loc[i,'user_id'], text=f"В голосовании приняли участие: {list_elections[:-2]}")
    elif "institut_like" in query.data:
        update.callback_query.message.delete()
        id_i = query.data.split('-')[1]
        mark = query.data.split('-')[2].replace("m", "-")
        user_triger[update.effective_chat.id] = {
            "triger": "institut",
            "id": id_i,
            "mark": mark
        }
        mark2 = "⭐️"
        if '-' in mark:
            mark2 = "👎"
        context.bot.send_message(chat_id=update.effective_chat.id, text = f"Тепрь прокоментируйте, почему именно {mark}{mark2}?")
    elif "institut" in query.data:
        if 'comments' == query.data.split('-')[1]:
            sms = ''
            for name in data['name_institut']:
                text = ''
                sum = 0
                info = pd.read_sql(f"SELECT * FROM institut WHERE name = '{name}';", engine)
                for i in range(len(info)):
                    mark2 = "⭐️"
                    if '-' in str(info.loc[i,'mark']):
                        mark2 = "👎"
                    text += f"{i+1}) {info.loc[i,'who']} ({info.loc[i,'name']} {abs(info.loc[i,'mark'])}{mark2}) - {info.loc[i,'comment']}\n"
                    sum += int(info.loc[i,'mark'])
                if text != '':
                    if sum < 0:
                        mark3 = "👎"
                    elif sum == 0:
                        mark3 = ""
                    elif sum > 0:
                        mark3 = "⭐️"
                    sms += f"🎓 {name} общая оценка {abs(sum)}{mark3}:\n{text}\n"
            context.bot.send_message(chat_id=update.effective_chat.id, text=sms)
        elif 'statistik' == query.data.split('-')[1]:
            sms = ''
            for name in data['name_institut']:
                sum = 0
                info = pd.read_sql(f"SELECT * FROM institut WHERE name = '{name}';", engine)
                for i in range(len(info)):
                    sum += int(info.loc[i,'mark'])
                if sum != 0:
                    if sum < 0:
                        mark3 = "👎"
                    elif sum > 0:
                        mark3 = "⭐️"
                    sms += f"🎓 {name} общая оценка {abs(sum)}{mark3}:\n"
            context.bot.send_message(chat_id=update.effective_chat.id, text=sms)
        else:
            button = [[InlineKeyboardButton("1⭐️", callback_data=f"institut_like-{query.data.split('-')[1]}-1"),
                      InlineKeyboardButton("2⭐️", callback_data=f"institut_like-{query.data.split('-')[1]}-2"),
                      InlineKeyboardButton("3⭐️", callback_data=f"institut_like-{query.data.split('-')[1]}-3"),
                      InlineKeyboardButton("4⭐️", callback_data=f"institut_like-{query.data.split('-')[1]}-4"),
                      InlineKeyboardButton("5⭐️", callback_data=f"institut_like-{query.data.split('-')[1]}-5")],
                      [InlineKeyboardButton("1👎", callback_data=f"institut_like-{query.data.split('-')[1]}-m1"),
                       InlineKeyboardButton("2👎", callback_data=f"institut_like-{query.data.split('-')[1]}-m2"),
                       InlineKeyboardButton("3👎", callback_data=f"institut_like-{query.data.split('-')[1]}-m3"),
                       InlineKeyboardButton("4👎", callback_data=f"institut_like-{query.data.split('-')[1]}-m4"),
                       InlineKeyboardButton("5👎", callback_data=f"institut_like-{query.data.split('-')[1]}-m5")]]
            context.bot.send_message(chat_id=update.effective_chat.id, text='Оцените институт по пятизвездочной системе.',
                                     reply_markup=InlineKeyboardMarkup(button))
    elif "call" == query.data:
        name = name_kids[update.effective_chat.id]
        engine.execute(f"INSERT INTO answer(date, name, answer_kids) VALUES('{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}','{name}','Да, позвонил(а)');")
        query.edit_message_text("Замечательно 😊")

def Timer(update, context,sec):
    time.sleep(sec)
    if update.effective_chat.id in user_triger:
        user_triger.pop(update.effective_chat.id)
def Timer_status(update, context,sec,msg_id):
    time.sleep(sec)
    try:
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg_id)
    except Exception:
        logging.info("Проблема с таймером")

def statistics(update, context):
    ########### Сбор информации ####################
    statistic = {}
    info = pd.read_sql(f"SELECT name, mark, antimark, star, poo, iq, brain, books_end FROM user_family WHERE access = 0;", engine)
    for i in range(len(info)):
        #Считываем из БД значения и присваиваем их к переменным
        like = int(info.loc[i, "mark"])
        star = int(info.loc[i, "star"])
        dislike = int(info.loc[i, "antimark"])
        poo = int(info.loc[i, "poo"])
        iq = int(info.loc[i, "iq"])
        brain = int(info.loc[i, "brain"])
        books_end_next = int(info.loc[i, "books_end"])//5
        books_end = int(info.loc[i, "books_end"]) - (books_end_next * 5)
        # Создаем строковые переменные в которые будем помещать изображения равное числу в переменной
        sms_like = "👍" * like
        sms_star = "⭐" * star
        sms_dislike = "👎" * dislike
        sms_poo = "💩" * poo
        sms_iq = "💡" * iq
        sms_brain = "🧠" * brain
        sms_books_end = "📕" * books_end
        sms_books_end_next = "🎓" * books_end_next
    ###########################################################
    ###########################################################
        # соотносим значения все значения с лайками складываем и получаем результат => у кого больше тот и на первом месте.
        result = (like+(star*100))+((brain*25)+(iq/2))
        statistic[info.loc[i, "name"]] = {
            "like": str(like) + sms_like,
            "dislike": str(dislike) + sms_dislike,
            "result": result,
            "star": str(star) + sms_star,
            "poo": str(poo) + sms_poo,
            "iq": str(iq) + sms_iq,
            "brain": str(brain) + sms_brain,
            "books_end": str(books_end) + sms_books_end,
            "books_end_next": str(books_end_next) + sms_books_end_next,
            "place": 0
        }
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
    ########### Выявления победителя и раставления по местам ####################
    ########### Вывод результатов ####################
    place1 = ""
    place2 = ""
    place3 = ""
    place4 = ""
    for i in range(len(info)):
        if statistic[info.loc[i, "name"]]["place"] == 1:
            place1 = f"🥇 👑{str(info.loc[i, 'name'])}👑\n{str(statistic[info.loc[i, 'name']]['like'])}"
            if str(statistic[info.loc[i, 'name']]['dislike']) != "0":
                place1 += "\n" +str(statistic[info.loc[i, 'name']]['dislike'])
            if str(statistic[info.loc[i, 'name']]['star']) != "0":
                place1 += "\n" + str(statistic[info.loc[i, 'name']]['star'])
            if str(statistic[info.loc[i, 'name']]['poo']) != "0":
                place1 += "\n" + str(statistic[info.loc[i, 'name']]['poo'])
            if str(statistic[info.loc[i, 'name']]['iq']) != "0":
                place1 += "\n" + str(statistic[info.loc[i, 'name']]['iq'])
            if str(statistic[info.loc[i, 'name']]['brain']) != "0":
                place1 += "\n" + str(statistic[info.loc[i, 'name']]['brain'])
            if str(statistic[info.loc[i, 'name']]['books_end']) != "0":
                place1 += "\n" + str(statistic[info.loc[i, 'name']]['books_end'])
            if str(statistic[info.loc[i, 'name']]['books_end_next']) != "0":
                place1 += "\n" + str(statistic[info.loc[i, 'name']]['books_end_next'])
        elif statistic[info.loc[i, "name"]]["place"] == 2:
            place2 = f"🥈 {str(info.loc[i, 'name'])}\n{str(statistic[info.loc[i, 'name']]['like'])}"
            if str(statistic[info.loc[i, 'name']]['dislike']) != "0":
                place2 += "\n" + str(statistic[info.loc[i, 'name']]['dislike'])
            if str(statistic[info.loc[i, 'name']]['star']) != "0":
                place2 += "\n" + str(statistic[info.loc[i, 'name']]['star'])
            if str(statistic[info.loc[i, 'name']]['poo']) != "0":
                place2 += "\n" + str(statistic[info.loc[i, 'name']]['poo'])
            if str(statistic[info.loc[i, 'name']]['iq']) != "0":
                place2 += "\n" + str(statistic[info.loc[i, 'name']]['iq'])
            if str(statistic[info.loc[i, 'name']]['brain']) != "0":
                place2 += "\n" + str(statistic[info.loc[i, 'name']]['brain'])
            if str(statistic[info.loc[i, 'name']]['books_end']) != "0":
                place2 += "\n" + str(statistic[info.loc[i, 'name']]['books_end'])
            if str(statistic[info.loc[i, 'name']]['books_end_next']) != "0":
                place2 += "\n" + str(statistic[info.loc[i, 'name']]['books_end_next'])
        elif statistic[info.loc[i, "name"]]["place"] == 3:
            place3 = f"🥉 {str(info.loc[i, 'name'])}\n{str(statistic[info.loc[i, 'name']]['like'])}"
            if str(statistic[info.loc[i, 'name']]['dislike']) != "0":
                place3 += "\n" + str(statistic[info.loc[i, 'name']]['dislike'])
            if str(statistic[info.loc[i, 'name']]['star']) != "0":
                place3 += "\n" + str(statistic[info.loc[i, 'name']]['star'])
            if str(statistic[info.loc[i, 'name']]['poo']) != "0":
                place3 += "\n" + str(statistic[info.loc[i, 'name']]['poo'])
            if str(statistic[info.loc[i, 'name']]['iq']) != "0":
                place3 += "\n" + str(statistic[info.loc[i, 'name']]['iq'])
            if str(statistic[info.loc[i, 'name']]['brain']) != "0":
                place3 += "\n" + str(statistic[info.loc[i, 'name']]['brain'])
            if str(statistic[info.loc[i, 'name']]['books_end']) != "0":
                place3 += "\n" + str(statistic[info.loc[i, 'name']]['books_end'])
            if str(statistic[info.loc[i, 'name']]['books_end_next']) != "0":
                place3 += "\n" + str(statistic[info.loc[i, 'name']]['books_end_next'])
        elif statistic[info.loc[i, "name"]]["place"] == 4:
            place4 = f"{str(info.loc[i, 'name'])}\n{str(statistic[info.loc[i, 'name']]['like'])}"
            if str(statistic[info.loc[i, 'name']]['dislike']) != "0":
                place4 += "\n" + str(statistic[info.loc[i, 'name']]['dislike'])
            if str(statistic[info.loc[i, 'name']]['star']) != "0":
                place4 += "\n" + str(statistic[info.loc[i, 'name']]['star'])
            if str(statistic[info.loc[i, 'name']]['poo']) != "0":
                place4 += "\n" + str(statistic[info.loc[i, 'name']]['poo'])
            if str(statistic[info.loc[i, 'name']]['iq']) != "0":
                place4 += "\n" + str(statistic[info.loc[i, 'name']]['iq'])
            if str(statistic[info.loc[i, 'name']]['brain']) != "0":
                place4 += "\n" + str(statistic[info.loc[i, 'name']]['brain'])
            if str(statistic[info.loc[i, 'name']]['books_end']) != "0":
                place4 += "\n" + str(statistic[info.loc[i, 'name']]['books_end'])
            if str(statistic[info.loc[i, 'name']]['books_end_next']) != "0":
                place4 += "\n" + str(statistic[info.loc[i, 'name']]['books_end_next'])
    message = place1 + "\n\n" + place2 + "\n\n" + place3 + "\n\n" + place4
    context.bot.send_message(chat_id=update.effective_chat.id,text=message)
    Thread(target=Timer_status, args=(update, context, 60, update.message.message_id+1)).start()

def statistics_like_year(update, context):
    ########### Сбор информации ####################
    month_name = {
        "1": "Январь",
        "2": "Февраль",
        "3": "Март",
        "4": "Апрель",
        "5": "Май",
        "6": "Июнь",
        "7": "Июль",
        "8": "Август",
        "9": "Сентябрь",
        "10": "Октябрь",
        "11": "Ноябрь",
        "12": "Декабрь"
    }
    message = ''
    info = pd.read_sql(f"SELECT name, month, star, poo, brain, place, books_end FROM statistics WHERE year = '{datetime.now().year}';", engine)
    if len(info) == 0: # Пока нет информации за этот год, будем выводить за тот. Следовательно в феврале будет только январь
        info = pd.read_sql(f"SELECT name, month, star, poo, brain, place, books_end FROM statistics WHERE year = '{int(datetime.now().year) - 1}';", engine)
    for j in range(12, 0,-1):
        text = ''
        place1 = ''
        place2 = ''
        place3 = ''
        place4 = ''
        for i in range(len(info)):
            if int(info.loc[i,"month"]) == j:
                if str(info.loc[i, 'books_end']) != "0":
                    books_end_next = int(info.loc[i, "books_end"]) // 5
                    books_end = int(info.loc[i, "books_end"]) - (books_end_next * 5)
                else:
                    books_end_next = 0
                    books_end = 0
                if int(info.loc[i, "place"]) == 1:
                    place1 = f"🥇{info.loc[i, 'name']} -"
                    if str(info.loc[i, 'star']) != "0":
                        place1 += f" {info.loc[i, 'star']}⭐"
                    if str(info.loc[i, 'poo']) != "0":
                        place1 += f" {info.loc[i, 'poo']}💩"
                    if str(info.loc[i, 'brain']) != "0":
                        place1 += f" {info.loc[i, 'brain']}🧠"
                    if str(books_end) != "0":
                        place1 += f" {books_end}📕"
                    if str(books_end_next) != "0":
                        place1 += f" {books_end_next}🎓"
                elif int(info.loc[i, "place"]) == 2:
                    place2 = f"🥈{info.loc[i, 'name']} -"
                    if str(info.loc[i, 'star']) != "0":
                        place2 += f" {info.loc[i, 'star']}⭐"
                    if str(info.loc[i, 'poo']) != "0":
                        place2 += f" {info.loc[i, 'poo']}💩"
                    if str(info.loc[i, 'brain']) != "0":
                        place2 += f" {info.loc[i, 'brain']}🧠"
                    if str(books_end) != "0":
                        place2 += f" {books_end}📕"
                    if str(books_end_next) != "0":
                        place2 += f" {books_end_next}🎓"
                elif int(info.loc[i, "place"]) == 3:
                    place3 = f"🥉{info.loc[i, 'name']} -"
                    if str(info.loc[i, 'star']) != "0":
                        place3 += f" {info.loc[i, 'star']}⭐"
                    if str(info.loc[i, 'poo']) != "0":
                        place3 += f" {info.loc[i, 'poo']}💩"
                    if str(info.loc[i, 'brain']) != "0":
                        place3 += f" {info.loc[i, 'brain']}🧠"
                    if str(books_end) != "0":
                        place3 += f" {books_end}📕"
                    if str(books_end_next) != "0":
                        place3 += f" {books_end_next}🎓"
                elif int(info.loc[i, "place"]) == 4:
                    place4 = f"🎗{info.loc[i, 'name']} -"
                    if str(info.loc[i, 'star']) != "0":
                        place4 += f" {info.loc[i, 'star']}⭐"
                    if str(info.loc[i, 'poo']) != "0":
                        place4 += f" {info.loc[i, 'poo']}💩"
                    if str(info.loc[i, 'brain']) != "0":
                        place4 += f" {info.loc[i, 'brain']}🧠"
                    if str(books_end) != "0":
                        place4 += f" {books_end}📕"
                    if str(books_end_next) != "0":
                        place4 += f" {books_end_next}🎓"
                text = f"{place1}\n{place2}\n{place3}\n{place4}"
        if text != '':
            message += f"{month_name[str(j)]}:\n{text}\n"
    if message != '':
        context.bot.send_message(chat_id=update.effective_chat.id,text=message)
        Thread(target=Timer_status, args=(update, context, 60, update.message.message_id+1)).start()

def fine_books(update, context):
    info = pd.read_sql_query(f"SELECT id, name, writer, book_name, all_page, every_day_page, old_page, new_page FROM books WHERE user_id = {update.effective_chat.id};", engine)
    if len(info) >= 1:
    #     id = info.loc[0, "id"]
    #     name = info.loc[0, 'name']
    #     old_page = int(info.loc[0, 'old_page'])
    #     book = info.loc[0, "book_name"] + "(" + info.loc[0, "writer"] + ")"
    #     every_day_page = info.loc[0, "every_day_page"]
    #     all_page = info.loc[0, "all_page"]
    #     books(update, context, id, name, old_page, book, every_day_page, all_page)
    # elif len(info) > 1:
        keyboard = []
        for i in range(len(info)):
            keyboard += [[InlineKeyboardButton('Книга "' + info.loc[i, "book_name"] + '"', callback_data='book-' + str(info.loc[i, "id"]))]]
        keyboard += [[InlineKeyboardButton('Добавить новую книгу', callback_data='book-0')]]
        context.bot.send_message(chat_id=update.effective_chat.id, text="Выберите книгу:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        keyboard = [[InlineKeyboardButton('Добавить новую книгу', callback_data='book-0')]]
        context.bot.send_message(chat_id=update.effective_chat.id, text="У тебя нет книг, но можно добавить.",
                                 reply_markup=InlineKeyboardMarkup(keyboard))

def books(update, context, id, name, old_page, book, every_day_page, all_page):
    page = ''
    if name == "Вова":
        read = "прочитал"
        stop = "остановился"
    else:
        read = "прочитала"
        stop = "остановилась"
    old_page_text = old_page
    if old_page > 20:
        old_page = int(str(old_page)[len(str(old_page)) - 1:])
    if old_page == 0 or (old_page >= 5 and old_page <= 20):
        page = "страниц"
    elif old_page >= 2 and old_page <= 4:
        page = "страницы"
    elif old_page == 1:
        page = "страница"
    reply_keyboard = [['Отмена']]
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Книга \"{book}\", по моим данным, ты {read} {old_page_text} {page}. Если с тех пор что-то изменилось, то напиши номер страницы на которой ты {stop}.",reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,one_time_keyboard=False))
    user_triger[update.effective_chat.id] ={
        "triger": "book",
        "id": id,
        "book": book,
        "old_page": old_page_text,
        "all_page": all_page,
        "every_day_page": every_day_page
    }
def time_yes(update, context):
    info = pd.read_sql_query(f"SELECT date, name,answer_kids FROM answer WHERE date > '{(datetime.now() - timedelta(weeks=+2)).strftime('%Y-%m-%d %H:%M:%S')}' AND answer_kids = 'Да' ORDER BY date ASC;",engine)
    sms = ''
    if len(info) != 0:
        for i in range(len(info)):
            sms += f"{info.loc[i,'date'].strftime('%d.%m.%y %H:%M')} - {info.loc[i,'name']} ответ \"{info.loc[i,'answer_kids']}\"\n"
    else:
        sms = "Сегодня ответов \"Да\" не было."
    context.bot.send_message(chat_id=update.effective_chat.id, text = sms)

def handle_text(update, context):
    if update.effective_chat.id in user_triger:
        if user_triger[update.effective_chat.id]["triger"] == 'token':
            num = user_triger[943180118]["num"]
            flow = user_triger[943180118]["flow"]
            print(update.message.text)
            credentials = flow.run_console_code(update.message.text)
            pickle.dump(credentials, open(f"{working_folder}calendar_tokens/token_{data_kids[kids[num]]}.pkl", "wb"))
            print(num)
            if num < 4:
                num += 1
                print(num)
                token_download(update, context, num)
            else:
                user_triger.pop(943180118)
                context.bot.send_message(chat_id=943180118, text="готово. Токены заменены.")
        elif user_triger[update.effective_chat.id]["triger"] == 'institut':
            engine.execute(f"INSERT INTO institut (name, mark, who, comment) VALUES('{data['name_institut'][int(user_triger[update.effective_chat.id]['id'])]}', '{user_triger[update.effective_chat.id]['mark']}', '{data[update.effective_chat.id]}', '{update.message.text}');")
            user_triger.pop(update.effective_chat.id)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Отлично. Я записал!")
        else:
            triger(update, context, user_triger, engine, start, user, logging, name_kids, papa, mama)
    else:
        search_result = engine.execute(f"SELECT name,access FROM user_family WHERE user_id = '{str(update.effective_chat.id)}' AND access in ('1', '2');").fetchall()
        if "книги" == update.message.text.lower():
            fine_books(update, context)
        elif "институт" == update.message.text.lower():
            button = []
            button2 = []
            for i in range(len(data['name_institut'])):
                button += [[InlineKeyboardButton(data['name_institut'][i], url=data['link_institut'][i])]]
                button2 += [[InlineKeyboardButton(data['name_institut'][i], callback_data=f"institut-{i}")]]
            button2 += [[InlineKeyboardButton("📖Почитать комментарии📚", callback_data=f"institut-comments")],[InlineKeyboardButton("📖Статистика📚", callback_data=f"institut-statistik")]]
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите группу для обсуждения:',
                                        reply_markup=InlineKeyboardMarkup(button))
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите институт чтобы поставить оценку.',
                                     reply_markup=InlineKeyboardMarkup(button2))
        elif "проблемы" == update.message.text.lower():
            reply_keyboard = [['Список проблем','Закрыть проблему'],['Отменить']]
            sms = 'Выбери посмотреть "Cписок проблем" или "Закрыть проблему"'
            context.bot.send_message(chat_id=update.effective_chat.id, text=sms, reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=False))
        elif "список проблем" == update.message.text.lower():
            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
            sms = ''
            info = pd.read_sql_query("SELECT id, name, msg_text, date FROM msg_list_work WHERE make = 0 ORDER BY date ASC;", engine)  #
            if len(info) != 0:
                for i in range(len(info)):
                    sms += str(info.loc[i, 'date'].strftime('%d.%m.%Y %H:%M')) + " " + str(info.loc[i, 'name']) + ' проблема №'+ str(info.loc[i, 'id']) +':\n"' + str(info.loc[i, 'msg_text']) + '"\n\n'
                context.bot.send_message(chat_id=update.effective_chat.id, text=sms)
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Проблем нет!")
        elif "закрыть проблему" == update.message.text.lower():
            try:
                keyboard = []
                info = pd.read_sql("SELECT id, name, msg_text, date FROM msg_list_work WHERE make = 0 ORDER BY date ASC;", engine)
                for i in range(len(info)):
                    keyboard += [[InlineKeyboardButton(f"Проблема №{str(info.loc[i, 'id'])}", callback_data='no_problem-' + str(info.loc[i, 'id']))]]
                context.bot.send_message(chat_id=update.effective_chat.id, text='Выбери номер решенной проблемы, чтобы закрыть:', reply_markup=InlineKeyboardMarkup(keyboard))
            except Exception as err:
                logging.error('Error:' + str(err))
        elif "статистика за год" == update.message.text.lower():
            statistics_like_year(update,context)
        elif "еда" == update.message.text.lower():
            eat(update, context, user_triger)
        elif "продукт" == update.message.text.lower():
            products(update, context, user_triger)
        elif "категории" == update.message.text.lower():
            categories(update, context, user_triger)
        elif "частота" == update.message.text.lower():
            frequency(update, context, user_triger)
        elif "блюдо" == update.message.text.lower():
            dish(update, context, user_triger)
            info = pd.read_sql("SELECT name FROM dish;", engine)
            if len(info) != 0:
                text = ''
                for i in range(len(info)):
                    text += f'{i + 1}) {info.loc[i, "name"]}\n'
                context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        elif 'отменить' == update.message.text.lower() or 'отмена' == update.message.text.lower() or 'отменить ввод' == update.message.text.lower()\
                or 'вернуться в главное меню' == update.message.text.lower() or 'вернуться в меню "еда"' == update.message.text.lower():
            if 'вернуться в главное меню' == update.message.text.lower():
                sms = 'хорошо, возвращаюсь.'
                user(update, context, sms)
            elif 'вернуться в меню "еда"' == update.message.text.lower():
                eat(update, context, user_triger)
            else:
                sms = 'хорошо, отмена.'
                user(update, context, sms)

###########################################################################################################################
#######################################    Для родителей    ###############################################################
###########################################################################################################################
        elif len(search_result) != 0: # Для родителей
            parents(update, context, user_triger, engine, statistics, Timer_status, kids, data_kids)
###########################################################################################################################
#######################################    Для детей    ###################################################################
###########################################################################################################################
        elif len(search_result) == 0:# Для детей
            children(update, context, user_triger, engine, statistics, name_kids, data_kids)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Я Вас не понимаю.")
####################################################
############# Обьявление заголовков ################
####################################################

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

time_yes_handler = CommandHandler('time_yes', time_yes)
dispatcher.add_handler(time_yes_handler)

mega_msg_handler = CommandHandler('mega_msg', mega_msg)
dispatcher.add_handler(mega_msg_handler)
#
token_handler = CommandHandler('token', token_download)
dispatcher.add_handler(token_handler)

text_handler = MessageHandler(Filters.text, handle_text)
dispatcher.add_handler(text_handler)

dispatcher.add_handler(CallbackQueryHandler(button))

####################################################
############# Обьявление заголовков ################
####################################################

updater.start_polling()