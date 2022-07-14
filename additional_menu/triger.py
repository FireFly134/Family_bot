# coding=UTF-8
import pandas as pd

from datetime import datetime
from time import sleep

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

from free_time import free_time

def eat(update, context, user_triger):
    if update.effective_chat.id in user_triger:
        user_triger.pop(update.effective_chat.id)
    reply_keyboard = [['Продукт', 'Категории', 'Частота'],['Блюдо']] #, 'Частота'],['добавить в корзину'],
    if update.effective_chat.id == 232749605 or update.effective_chat.id == 943180118:
        reply_keyboard += [['Список для покупки', 'Повторить опрос для покупок'], ['Вернуться в главное меню']]
    else:
        reply_keyboard += [['Вернуться в главное меню']]
    sms = "Тут можно добавить новый 'Продукт', 'Категорию' или изменить периодичность заказа продуктов."
    context.bot.send_message(chat_id=update.effective_chat.id, text=sms,
                             reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                              one_time_keyboard=False))
def products(update, context, user_triger):
    reply_keyboard = [['Добавить новый продукт', 'Добавить продукт в корзину', 'Удалить продукт'], ['Изменить ссылку на продукт', 'Посмотреть продукты'], ['Вернуться в меню "ЕДА"']]
    user_triger[update.effective_chat.id] = {
        'triger': "products",
        'New': False,
        'Delete': False,
        'Edit_link': False,
        'step': 0,
        'categories': 'None',
        'choice': 'None',
        'name': 'None',
        'link': 'None'
    }
    sms = "Манипуляции с продуктами"
    context.bot.send_message(chat_id=update.effective_chat.id, text=sms,
                             reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                              one_time_keyboard=False))
def categories (update, context, user_triger):
    reply_keyboard = [['Добавить новую категорию', 'Удалить категорию', 'Посмотреть категории'], ['Вернуться в меню "ЕДА"']]
    user_triger[update.effective_chat.id] = {
        'triger': "categories",
        'New': False,
        'Delete': False
    }
    sms = "Манипуляции с категориями продуктов"
    context.bot.send_message(chat_id=update.effective_chat.id, text=sms,
                             reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                              one_time_keyboard=False))
def frequency (update, context, user_triger):
    reply_keyboard = [['Изменить', 'Проверить'], ['Вернуться в меню "ЕДА"']]
    user_triger[update.effective_chat.id] = {
        'triger': "frequency",
        'Edit': False,
        'edit_products': False,
        'categories': 'None',
        'name': 'None',
        'step': 0
    }
    sms = "Тут можно проверить или изменить периодичность заказа данных продуктов."
    context.bot.send_message(chat_id=update.effective_chat.id, text=sms,
                             reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                              one_time_keyboard=False))
def dish(update, context, user_triger):
    reply_keyboard = [['Создать набор для блюда', 'Посмотреть набор для блюда', 'Добавить набор в корзину'], ["Добавить рецепт", "Посмотреть рецепт"], ["Удалить блюдо", "Удалить рецепт"],['Вернуться в меню "ЕДА"']]
    user_triger[update.effective_chat.id] = {
        'triger': "dish",
        'create': False,
        'add_note': False,
        'show_note': False,
        'show_product': False,
        'delete': 'None',
        'name': 'None',
        'num_need_people': 1,
        'coocing_time': 0,
        'step': 0,
        'list_products': []
    }
    sms = "В данном разделе можно выбрать продукты для приготовления выбранного блюда за один раз. Так же можно создать блюдо и выбрать набор продуктов для приготовления."
    context.bot.send_message(chat_id=update.effective_chat.id, text=sms,
                             reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                              one_time_keyboard=False))

def handle_text(update, context, user_triger, engine, start, user, logging, name_kids, papa, mama):
    triger = user_triger[update.effective_chat.id]["triger"]
    if triger == "reg":
        if "андрей" == update.message.text.lower():
            name = "Андрей"
        elif "амира" == update.message.text.lower():
            name = "Амира"
        elif "лиза" == update.message.text.lower():
            name = "Лиза"
        elif "лейла" == update.message.text.lower():
            name = "Лейла"
        elif "вова" == update.message.text.lower():
            name = "Вова"
        elif "инна" == update.message.text.lower():
            name = "Инна"
        elif "константин" == update.message.text.lower():
            name = "Константин"
        elif "валя" == update.message.text.lower():
            name = "Бабушка Валя"
        elif "дима" == update.message.text.lower():
            name = "Дедушка Дима"
        elif "людмила" == update.message.text.lower():
            name = "Бабушка Людмила"
        search_result = engine.execute(f"SELECT name,access FROM user_family WHERE name = '{name}';").fetchall()
        if len(search_result) != 0:
            engine.execute("UPDATE user_family SET user_id = " + str(update.effective_chat.id) + " WHERE name = '" + name+"';")
            user_triger.pop(update.effective_chat.id)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Ой, простите, сразу не узнал! Такого больше не повторится. 😁")
            start(update,context)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Простите, я не знаю такого имени, попробуйте еще раз. 😁")
    #В случае если еа вопрос ответ -"НЕТ" то слудующий вопрос почему нет? и переходим сюда, ждем написания ответа и затем сохраняем его.
    elif triger == "comment":
        engine.execute(f"UPDATE user_family SET comment = '{update.message.text}' WHERE user_id = '{update.effective_chat.id}';")
        context.bot.send_message(chat_id=update.effective_chat.id, text="Спасибо.😊")
        context.bot.send_message(chat_id=papa, text=user_triger[update.effective_chat.id]["name"] + "(Ответ НЕТ)")
        user_triger.pop(update.effective_chat.id)
    # Тригер "я хочу похвалу" срабатывает после нажатия кнопки и ждет ответ чем ребенок хочет похвалиться перед родителями
    elif triger == "i_want_praise":
        if 'отменить' == update.message.text.lower():
            user_triger.pop(update.effective_chat.id)
            user(update,context,'хорошо, отмена.')
            logging.info('"хочу похвалу", отмена.')
        elif 'хочу похвалу' == update.message.text.lower():# Не знаю как но было дело что по несколько раз писалось это сообщение и всместо того чем хочет поделиться приходило это...'хочу похвалу'
            context.bot.send_message(chat_id=update.effective_chat.id, text="Да-да, я понял... Напиши о своих достижениях и я это передам твоим родителям :)")
        else:
            info = pd.read_sql_query(f"SELECT name FROM user_family WHERE user_id = '{update.effective_chat.id}';",engine)
            name = str(info.loc[0, 'name'])
            if user_triger[update.effective_chat.id]["skill"]:
                yes = 'IQ_Yes'
                smile = '💡'
                mark = 'IQ'
                logging.info("хочу похвалу за СКИЛЛ " + name + ':\n"' + str(update.message.text) + '"')
            else:
                yes = 'yes'
                smile = '👍'
                mark = 'mark'
                logging.info("хочу похвалу " + name + ':\n"' + str(update.message.text) + '"')
            engine.execute(f"INSERT INTO msg_list(name, msg_text, date, user_id, kids) VALUES('{name}','{str(update.message.text)}','{str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}','{str(update.effective_chat.id)}','{yes}');")
            keyboard = []
            for i in range(1, 6):
                keyboard += [InlineKeyboardButton(f'{i}{smile}', callback_data=f'{mark}-{name}-{i}')]
            context.bot.send_message(chat_id=papa, text=name +':\n"'+str(update.message.text)+'"', reply_markup=InlineKeyboardMarkup([keyboard]))
            context.bot.send_message(chat_id=mama, text=name +':\n"'+str(update.message.text)+'"', reply_markup=InlineKeyboardMarkup([keyboard]))
            recipient = pd.read_sql_query(f"SELECT name, user_id FROM user_family WHERE access = '2';", engine)
            for i in range(len(recipient)):
                try:
                    context.bot.send_message(chat_id=int(recipient.loc[i, 'user_id']), text= name + ':\n"' + str(update.message.text) + '"')
                except Exception:
                    logging.error(f"{recipient.loc[i, 'name']} не смог отправить смс 'хочу похвалу'")
            user_triger.pop(update.effective_chat.id)
            user(update, context, 'Отправил!')
            logging.info('Родителям отправил!')
            sleep(2)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Родители очень заняты, не всегда есть время ответить в эту же секунду. Я отправлю им все твои сообщения и постараюсь напомнить чтобы они не забыли тебя похвалить))")
    elif triger == "problem":
        if 'отменить' == update.message.text.lower():
            user_triger.pop(update.effective_chat.id)
            user(update, context, 'хорошо, отмена.')
            logging.info('"сообщить о проблеме", отмена.')
        elif 'сообщить о проблеме' == update.message.text.lower():
            context.bot.send_message(chat_id=update.effective_chat.id, text="Да-да, я понял... Опишите, в чём проблема.")
        else:
            info = pd.read_sql_query(f"SELECT name FROM user_family WHERE user_id = '{update.effective_chat.id}';",engine)
            name = str(info.loc[0, 'name'])
            engine.execute("INSERT INTO msg_list_work(name, msg_text, date, user_id, make) VALUES('" + name + "','" + str(update.message.text) + "','" + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "','" + str(update.effective_chat.id) + "','0');")
            context.bot.send_message(chat_id=462169878, text="Новое сообщение о проблеме! "+ name + ':\n"' + str(update.message.text) + '"')
            logging.info("Новое сообщение о проблеме! " + name + ':\n"' + str(update.message.text) + '"')
            user_triger.pop(update.effective_chat.id)
            user(update, context, 'Отправил!')
            logging.info("Вове отправил!")
###################################################################################################################
###################################################################################################################
###################################################################################################################
    # Родители пишут сами о успехе ребенка(освоении нового "скила") или на оборот и вручают за это оценку (лайк, дизлайк или IQ)
    elif triger == "assess":
        if user_triger[update.effective_chat.id]["name"] == "None" and 'отменить' != update.message.text.lower():
            kids_name = ""
            if 'амира' == update.message.text.lower() or 'амиру' == update.message.text.lower():
                context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
                kids_name = "Амира"
            elif 'лиза' == update.message.text.lower() or 'лизу' == update.message.text.lower():
                context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
                kids_name = "Лиза"
            elif 'лейла' == update.message.text.lower() or 'лейлу' == update.message.text.lower():
                context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
                kids_name = "Лейла"
            elif 'вова' == update.message.text.lower() or 'вову' == update.message.text.lower():
                context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
                kids_name = "Вова"
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Я не знаю таких детей. Выбирете повторно ребенка или нажмите кнопку \"Отменить\".")
            if kids_name != "":
                user_triger[update.effective_chat.id]["name"] = kids_name
                if user_triger[update.effective_chat.id]["skill"]:
                    user_triger[update.effective_chat.id]["choice"] = "IQ"
                    if user_triger[update.effective_chat.id]["name"] != "Вова":
                        a = 'a'
                    else:
                        a = ''
                    sms = f"Опишите, какой новый 'skill' освоил{a} {user_triger[update.effective_chat.id]['name']}?"
                    reply_keyboard = [['Отменить']]
                else:
                    reply_keyboard = [['Лайк👍', 'Дизлайк👎'], ['Отменить']]
                    sms = "Что ставим? Лайки или Дизлайки?"
                context.bot.send_message(chat_id=update.effective_chat.id, text=sms,reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,one_time_keyboard=False))
        elif user_triger[update.effective_chat.id]["choice"] == "None" and 'отменить' != update.message.text.lower():
            choice = ""
            if 'лайк👍' == update.message.text.lower() or 'лайк' == update.message.text.lower():
                context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
                choice = "лайк"
            elif 'дизлайк👎' == update.message.text.lower() or 'дизлайк' == update.message.text.lower():
                context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
                choice = "дизлайк"
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Я такую единицу одобрения не знаю. Выбирете повторно \"Лайк👍\" или \"Дизлайк👎\", или нажмите кнопку \"Отменить\".")
            if choice != "":
                user_triger[update.effective_chat.id]["choice"] = choice
                if user_triger[update.effective_chat.id]["name"] != "Вова":
                    a = 'a'
                    b = 'ась'
                else:
                    a = ''
                    b = 'ся'
                if choice == "лайк":
                    sms = f"Опишите, что хорошего совершил{a} {user_triger[update.effective_chat.id]['name']}."
                else:
                    sms = f"Опишите, в чем провинил{b} {user_triger[update.effective_chat.id]['name']}."
                reply_keyboard = [['Отменить']]
                context.bot.send_message(chat_id=update.effective_chat.id,text=sms,reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,one_time_keyboard=False))
        elif user_triger[update.effective_chat.id]["text"] == "None" and 'отменить' != update.message.text.lower():
            name = user_triger[update.effective_chat.id]["name"]
            choice = user_triger[update.effective_chat.id]["choice"]
            user_triger[update.effective_chat.id]["text"] = text = update.message.text
            info = pd.read_sql_query(f"SELECT user_id FROM user_family WHERE name = '{name}';", engine)
            if choice == "IQ":
                kid = 'IQ'
            else:
                kid = 'no'
            engine.execute(f"INSERT INTO msg_list(name, msg_text, date, user_id, kids) VALUES('{name}','{str(update.message.text)}','{str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}','{str(info.loc[0, 'user_id'])}','{kid}')")
            if choice == "лайк":
                smile = '👍'
                mark = 'mark'
            elif choice == "IQ":
                smile = '💡'
                mark = 'IQ'
            else:
                smile = '👎'
                mark = 'antimark'
            keyboard = []
            for i in range(1, 6):
                keyboard += [InlineKeyboardButton(f'{i}{smile}', callback_data=f'{mark}-{name}-{i}')]
            context.bot.send_message(chat_id=papa, text=name + ':\n"' + str(update.message.text) + '"',reply_markup=InlineKeyboardMarkup([keyboard]))
            context.bot.send_message(chat_id=mama, text=name + ':\n"' + str(update.message.text) + '"',reply_markup=InlineKeyboardMarkup([keyboard]))
            if update.effective_chat.id == papa:
                kto = "Папа:\n"
            elif update.effective_chat.id == mama:
                kto = "Мама:\n"
            logging.info(kto+"-"+name + ':"' + str(update.message.text)+'"')
            context.bot.send_message(chat_id=int(info.loc[0, "user_id"]), text=kto + str(update.message.text))
            user_triger.pop(update.effective_chat.id)
        elif 'отменить' == update.message.text.lower():
            user(update, context, 'хорошо, отмена.')
###################################################################################################################
###################################################################################################################
###################################################################################################################
    elif triger == "book":
        if 'отменить' == update.message.text.lower() or 'отмена' == update.message.text.lower():
            user(update, context, 'хорошо, отмена.')
        else:
            id = user_triger[update.effective_chat.id]["id"]
            every_day_page = user_triger[update.effective_chat.id]["every_day_page"]
            old_page = user_triger[update.effective_chat.id]["old_page"]
            all_page = user_triger[update.effective_chat.id]["all_page"]
            if update.message.text.isnumeric():
                if all_page > int(update.message.text):
                    if old_page < int(update.message.text):
                        new_page = int(update.message.text)
                        engine.execute(f"UPDATE books SET new_page = {new_page} WHERE id = {id};")
                        result = new_page - old_page
                        if every_day_page <= result:
                            text = "Хорошая работа, прочитано страниц - " + str(result)
                        else:
                            text = "прочитано страниц - " + str(result)

                    else:
                        text = "что-то тут не сходится... было же " + str(old_page)+"!"
                elif all_page == int(update.message.text):
                    text = "Ого, уже всё? Вот держи! +📕 Так держать! 🙂"
                    info = pd.read_sql(f"SELECT name, books_end FROM user_family WHERE user_id = '{update.effective_chat.id}';",engine)
                    books_end = int(info.loc[0,"books_end"]) +1
                    engine.execute(f"UPDATE books SET user_id = '0', status = 'прочитано', new_page = '{int(update.message.text)}' WHERE id = '{id}';")#name = 'Прочитано({info.loc[0,'name']})'
                    engine.execute(f"UPDATE user_family SET books_end = {books_end} WHERE user_id = '{update.effective_chat.id}';")
                    print(f"UPDATE user_family SET books_end = {books_end} WHERE user_id = '{update.effective_chat.id}';")
                    context.bot.send_message(chat_id=papa,text=f"{info.loc[0,'name']} +📕 за прочтённую книгу.")
                    context.bot.send_message(chat_id=mama, text=f"{info.loc[0, 'name']} +📕 за прочтённую книгу.")
                else:
                    text = "что-то тут не сходится... всего страниц же " + str(all_page) + "!"
                user_triger.pop(update.effective_chat.id)
                user(update,context,text)
            else:
                context.bot.send_message(chat_id=update.effective_chat.id,text="Мне нужен номер страницы цифрами.")
    elif triger == "add_book":
        if 'отменить' == update.message.text.lower() or 'отмена' == update.message.text.lower():
            user(update, context, 'хорошо, отмена.')
        elif 'да' == update.message.text.lower() or 'да, добавить' == update.message.text.lower():
            name = name_kids[update.effective_chat.id]
            engine.execute(f"INSERT INTO books(name, book_name, writer, all_page, user_id) "
                           f"VALUES('{name}',"
                                  f"'{user_triger[update.effective_chat.id]['name_book']}',"
                                  f"'{user_triger[update.effective_chat.id]['name_writer']}',"
                                  f"'{user_triger[update.effective_chat.id]['all_page']}',"
                                  f"'{update.effective_chat.id}');")
            info = pd.read_sql_query(f"SELECT id FROM books WHERE  name = '{name}' AND writer = '{user_triger[update.effective_chat.id]['name_writer']}' AND book_name = '{user_triger[update.effective_chat.id]['name_book']}';",engine)
            text = f"Добавлена книга для {str(name)[:len(str(name)) - 1]}ы:\nНазвание книги - \"{user_triger[update.effective_chat.id]['name_book']}\"\nАвтор - \"{user_triger[update.effective_chat.id]['name_writer']}\"\nВсего страниц в книге = {user_triger[update.effective_chat.id]['all_page']}\n"
            logging.info(text)
            keyboard = [[InlineKeyboardButton(f'Установить суточную норму для {str(name)[:len(name)-1]}ы', callback_data='add_book-' + str(info.loc[0,'id']))]]
            context.bot.send_message(chat_id=papa, text=text, reply_markup=InlineKeyboardMarkup(keyboard))
            user(update, context, "Книга добавлена, приятного прочтения!")
            logging.info(text+"\nКнига добавлена, приятного прочтения! И пошло на подтверждение.")
        else:
            user_msg = update.message.text
            if user_triger[update.effective_chat.id]["name_book"] == "None":
                user_triger[update.effective_chat.id]["name_book"] = str(user_msg)
                context.bot.send_message(chat_id=update.effective_chat.id, text="Кто автор этой книги?")
            elif user_triger[update.effective_chat.id]["name_writer"] == "None":
                user_triger[update.effective_chat.id]["name_writer"] = str(user_msg)
                context.bot.send_message(chat_id=update.effective_chat.id, text="И на последок, сколько страниц в этой книге?")
            elif user_triger[update.effective_chat.id]["all_page"] == "None":
                if user_msg.isnumeric():
                    if int(user_msg) > 0:
                        user_triger[update.effective_chat.id]["all_page"] = user_msg
                        reply_keyboard = [['Да, добавить','Отменить']]
                        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Название книги - "{user_triger[update.effective_chat.id]["name_book"]}"\n'
                                                                                        f'Автор - "{user_triger[update.effective_chat.id]["name_writer"]}"\n'
                                                                                        f'Всего страниц в книге = {user_triger[update.effective_chat.id]["all_page"]}\n'
                                                                                        f'Всё верно?',
                                                                                        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=False))
                    else:
                        context.bot.send_message(chat_id=update.effective_chat.id, text="Введите верное количество страниц. Попробуйте еще раз.")
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Если я не ошибаюсь, страницы нумеровались цифрами). Попробуйте еще раз.")
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Если все верно, нажмите \"Да\"!")
    elif triger == "norma_for_new_book":
        user_msg = update.message.text
        if user_msg.isnumeric():
            if int(user_msg) > 0:
                engine.execute(f"UPDATE books SET every_day_page = {user_msg} WHERE id = '{user_triger[update.effective_chat.id]['book_id']}';")
                logging.info(f"every_day_page = {user_msg} WHERE book_id = '{user_triger[update.effective_chat.id]['book_id']}")
                user(update,context,"Суточная норма установлена.")
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Введите верное количество страниц. Попробуйте еще раз.")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Если я не ошибаюсь, страницы нумеровались цифрами). Попробуйте еще раз.")

###################################################################################################################
###################################################################################################################
###################################################################################################################
    elif triger == "free_time":
        if 'отменить' == update.message.text.lower() or 'отмена' == update.message.text.lower():
            user(update, context, 'хорошо, отмена.')
        else:
            if 'амира' == update.message.text.lower():
                context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
                text = free_time("Amira", "Амира", user_triger[update.effective_chat.id]['week'])
                user(update, context, text)
            elif 'лиза' == update.message.text.lower():
                context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
                text = free_time("Lisa", "Лиза", user_triger[update.effective_chat.id]['week'])
                user(update, context, text)
            elif 'лейла' == update.message.text.lower():
                context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
                text = free_time("Leila", "Лейла", user_triger[update.effective_chat.id]['week'])
                user(update, context, text)
            elif 'вова' == update.message.text.lower():
                context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
                text = free_time("Vova", "Вова", user_triger[update.effective_chat.id]['week'])
                user(update, context, text)
###################################################################################################################
###################################################################################################################
###################################################################################################################
    elif triger == "case":
        if 'вернуться в главное меню' == update.message.text.lower():
            user(update, context, 'хорошо, возвращаюсь.')
        else:
            reply_keyboard = [['Вернуться в главное меню']]
            if 'завершить выполнение' == update.message.text.lower():
                context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
                user_triger[update.effective_chat.id]["close"]=True
                user_triger[update.effective_chat.id]["cancel"] = False
                user_triger[update.effective_chat.id]["choice"] = False
                context.bot.send_message(chat_id=update.effective_chat.id, text="Введи номер задачи цифрами, для завершения работы с ней.", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=False))
            elif 'отменить выполнение' == update.message.text.lower():
                context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
                user_triger[update.effective_chat.id]["close"] = False
                user_triger[update.effective_chat.id]["cancel"] = True
                user_triger[update.effective_chat.id]["choice"] = False
                context.bot.send_message(chat_id=update.effective_chat.id, text="Введи номер задачи цифрами, для отмены выполнения.", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=False))
            elif 'выбрать еще...' == update.message.text.lower() or 'выбрать задание' == update.message.text.lower():
                user_triger[update.effective_chat.id]["close"] = False
                user_triger[update.effective_chat.id]["cancel"] = False
                user_triger[update.effective_chat.id]["choice"] = True
                if str(update.effective_chat.id) != "462169878":
                    info = pd.read_sql_query(f"SELECT id, name_case, num_of_likes FROM list_cases WHERE repeated_date <= '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}' AND name = '0';",engine)
                else:
                    info = pd.read_sql_query(f"SELECT id, name_case, num_of_likes FROM list_cases WHERE repeated_date <= '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}' AND name = '0' AND for_vova = 'True';",engine)
                sms = ''
                if len(info) != 0:
                    user_triger[update.effective_chat.id]["choice"] = True
                    user_triger[update.effective_chat.id]["case_id"] = {}
                    for i in range(len(info)):
                        sms += f"{i+1}) {info.loc[i,'name_case']} - награда {info.loc[i,'num_of_likes']}👍\n"
                        user_triger[update.effective_chat.id]["case_id"][i + 1] = info.loc[i, 'id']
                    context.bot.send_message(chat_id=update.effective_chat.id, text=sms, reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=False))
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Введи номер задачи цифрами, чтобы забрать себе для выполнения.")
                else:
                    user_triger[update.effective_chat.id]["choice"] = False
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Новых заданий нет.")
            elif update.message.text.isnumeric() and (user_triger[update.effective_chat.id]["cancel"] or user_triger[update.effective_chat.id]["close"] or user_triger[update.effective_chat.id]["choice"]):
                if len(user_triger[update.effective_chat.id]["case_id"]) >= int(update.message.text) and int(update.message.text) > 0:
                    id = user_triger[update.effective_chat.id]["case_id"][int(update.message.text)]
                    info = pd.read_sql_query(f"SELECT name_case, name, num_of_likes, random, access_denied FROM list_cases WHERE id = '{id}';", engine)
                    if user_triger[update.effective_chat.id]["close"]:# Закрываем задачу
                        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id - 1)
                        name = name_kids[update.effective_chat.id]
                        text = "Готово, задача будет закрыта после подтверждения родителей."
                        keyboard = [[InlineKeyboardButton('Да👍', callback_data=f'case-{id}-{update.effective_chat.id}-yes'),
                                     InlineKeyboardButton('Нет', callback_data=f'case-{id}-{update.effective_chat.id}-no')]]
                        context.bot.send_message(chat_id=papa, text=name + ': "' + str(info.loc[0,"name_case"]) + '"\nЗадача выполнена?',reply_markup=InlineKeyboardMarkup(keyboard))
                        context.bot.send_message(chat_id=mama, text=name + ': "' + str(info.loc[0,"name_case"]) + '"\nЗадача выполнена?',reply_markup=InlineKeyboardMarkup(keyboard))
                    elif user_triger[update.effective_chat.id]["cancel"]:# Отмена выполнения
                        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id - 1)
                        if info.loc[0,'access_denied'] != 'random':
                            print(info.loc[0,'random'])
                            engine.execute(f"UPDATE list_cases SET name = '0' WHERE id = '{id}';")
                            text = "Готово, задача отменена."
                        else:
                            text = "Отменить или оказаться не получится, но можно с кем-то поменяться."
                    elif user_triger[update.effective_chat.id]["choice"]:#Выбор нового задания
                        if str(info.loc[0, 'name']) == '0':
                            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id - 2)
                            engine.execute(f"UPDATE list_cases SET name = '{name_kids[update.effective_chat.id]}', antiduble = 0, access_denied = 'self' WHERE id = '{id}';")
                            text = f"Готово, задача \"{info.loc[0,'name_case']}\" присвоена."
                        else:
                            text = f"Ой, задача \"{info.loc[0, 'name_case']}\" ужа занята {str(info.loc[0, 'name'])[:len(str(info.loc[0, 'name']))-1]}ой.\nПопробуй выбрать что-то другое."
                    logging.info(f'{name_kids[update.effective_chat.id]} - {text}')
                    user(update, context, text)
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Такого номераа нет, попробуй еще раз)")
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Введи номер задачи цифрами!")
###################################################################################################################
###################################################################################################################
###################################################################################################################
    # elif triger == 'token':
    #     num = user_triger[943180118]["num"]
    #     flow = user_triger[943180118]["flow"]
    #     credentials = flow.run_console_code(update.message.text)
    #     pickle.dump(credentials, open(f"calendar_tokens/token_{data_kids[kids[num]]}.pkl", "wb"))
    #     if num < 4:
    #         num += 1
    #         token_download(update, context, num)
    elif triger == 'mega_msg':
        search_result = pd.read_sql_query(f"SELECT name,access,user_id FROM user_family WHERE access = 0;", engine)
        for i in range(len(search_result)):
            if str(search_result.loc[
                       i, 'access']) == "0":  # update.effective_chat.id == 232749605 or update.effective_chat.id == 943180118:
                try:
                    context.bot.send_message(chat_id=int(search_result.loc[i, 'user_id']), text=update.message.text)
                    logging.info(f'{str(search_result.loc[i, "name"])} - Сообщение получено. send_mega_msg()')
                except Exception:
                    logging.info(f'{str(search_result.loc[i, "name"])} - Сообщение не получено. send_mega_msg()')
###################################################################################################################
####################                       Функционал ЕДА                            ##############################
###################################################################################################################
    #Все дествия с продуктами
    elif triger == 'products':
        categories_pd = pd.read_sql_query("SELECT name FROM categories ORDER BY name ASC;", engine)
        if 'вернуться в меню "еда"' == update.message.text.lower():
            eat(update, context, user_triger)
        elif 'отменить' == update.message.text.lower() or 'отмена' == update.message.text.lower() or 'прекратить ввод' == update.message.text.lower():
            globals()[triger](update, context, user_triger)
        elif 'добавить продукт в корзину' == update.message.text.lower():
            info_categories = pd.read_sql(f"SELECT * FROM categories;", engine)
            keyboard = []
            for k in range(len(info_categories)):
                keyboard += [[InlineKeyboardButton(info_categories.loc[k, 'name'],
                                                   callback_data='query_for_buy_products-' + str(info_categories.loc[k, 'name']))]]
            sms = "Что необходимо приобрести?"
            context.bot.send_message(chat_id=update.effective_chat.id, text=sms, reply_markup=InlineKeyboardMarkup(keyboard))
        elif "добавить новый продукт" == update.message.text.lower():
            user_triger[update.effective_chat.id]['New'] = True
            user_triger[update.effective_chat.id]['Delete'] = False
            user_triger[update.effective_chat.id]['Edit_link'] = False
            context.bot.send_message(chat_id=update.effective_chat.id, text="Введите название продукта.",
                             reply_markup=ReplyKeyboardMarkup([['Отменить']], resize_keyboard=True,
                                                              one_time_keyboard=False))
        elif "удалить продукт" == update.message.text.lower() or "посмотреть продукты" == update.message.text.lower() or 'изменить ссылку на продукт' == update.message.text.lower():
            if "удалить продукт" == update.message.text.lower():
                user_triger[update.effective_chat.id]['choice'] = 'delete'
            elif 'изменить ссылку на продукт' == update.message.text.lower():
                user_triger[update.effective_chat.id]['choice'] = 'edit_link'
            else:
                user_triger[update.effective_chat.id]['choice'] = 'show'
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Выберите категорию,введите номер цифрами.",
                                     reply_markup=ReplyKeyboardMarkup([['Отменить']], resize_keyboard=True,
                                                                      one_time_keyboard=False))
            text = ''
            for i in range(len(categories_pd)):
                text += f'{i + 1}) {categories_pd.loc[i, "name"]}\n'
            context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        elif user_triger[update.effective_chat.id]['choice'] != 'None' and user_triger[update.effective_chat.id]['categories'] == 'None':
            if update.message.text.isnumeric():
                if int(update.message.text) <= len(categories_pd) and int(update.message.text) > 0:
                    user_triger[update.effective_chat.id]['categories'] = categories_pd.loc[int(update.message.text)-1, 'name']
                    products_pd = pd.read_sql_query(f"SELECT name, link FROM products WHERE categories = '{user_triger[update.effective_chat.id]['categories']}';",engine)
                    if len(products_pd) != 0:
                        if "delete" == user_triger[update.effective_chat.id]['choice']:
                            user_triger[update.effective_chat.id]['New'] = False
                            user_triger[update.effective_chat.id]['Delete'] = True
                            user_triger[update.effective_chat.id]['Edit_link'] = False
                            context.bot.send_message(chat_id=update.effective_chat.id,
                                                     text="Введите номер продукта, цифрами, чтобы удалить.",
                                                     reply_markup=ReplyKeyboardMarkup([['Отменить']],
                                                                                      resize_keyboard=True,
                                                                                      one_time_keyboard=False))
                        elif "edit_link" == user_triger[update.effective_chat.id]['choice']:
                            user_triger[update.effective_chat.id]['New'] = False
                            user_triger[update.effective_chat.id]['Delete'] = False
                            user_triger[update.effective_chat.id]['Edit_link'] = True
                            context.bot.send_message(chat_id=update.effective_chat.id,
                                                     text="Введите номер продукта, цифрами, чтобы изменить ссылку.",
                                                     reply_markup=ReplyKeyboardMarkup([['Отменить']],
                                                                                      resize_keyboard=True,
                                                                                      one_time_keyboard=False))

                        text = ''
                        for i in range(len(products_pd)):
                            text += f"{i + 1}) {products_pd.loc[i, 'name']} ({products_pd.loc[i, 'link']})\n"
                        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
                        if "show" == user_triger[update.effective_chat.id]['choice']:
                            globals()[triger](update, context, user_triger)
                    else:
                        context.bot.send_message(chat_id=update.effective_chat.id, text="Продуктов нет.")
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Такого номера нет! Выберите повторно из списка. К какой категории относится товар?")
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Введите номер категории цифрами, чтобы выбрать.")
        else:
            if user_triger[update.effective_chat.id]['New'] or user_triger[update.effective_chat.id]['Delete'] or user_triger[update.effective_chat.id]['Edit_link']:
                if user_triger[update.effective_chat.id]['New']:
                    #### ШАГ № 0 (первый :)) ####
                    if user_triger[update.effective_chat.id]['step'] == 0:
                        user_triger[update.effective_chat.id]['step'] = 1
                        user_triger[update.effective_chat.id]['name'] = update.message.text
                        context.bot.send_message(chat_id=update.effective_chat.id, text="Введите ссылку на продукт.",
                             reply_markup=ReplyKeyboardMarkup([['Отменить']], resize_keyboard=True,
                                                              one_time_keyboard=False))
                    #### ШАГ № 1  ####
                    elif user_triger[update.effective_chat.id]['step'] == 1:
                        user_triger[update.effective_chat.id]['step'] = 2
                        user_triger[update.effective_chat.id]['link'] = update.message.text
                        context.bot.send_message(chat_id=update.effective_chat.id, text="Выберите из списка. К какой категории относится товар?",
                             reply_markup=ReplyKeyboardMarkup([['Отменить']], resize_keyboard=True,
                                                              one_time_keyboard=False))
                        text = ''
                        for i in range(len(categories_pd)):
                            text += f'{i + 1}) {categories_pd.loc[i,"name"]}\n'
                        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
                        #### ШАГ № 2  ####
                    elif user_triger[update.effective_chat.id]['step'] == 2:
                        if update.message.text.isnumeric():
                            if int(update.message.text) <= len(categories_pd) and int(update.message.text) > 0:
                                engine.execute(f"INSERT INTO products(name, link, categories) VALUES('{user_triger[update.effective_chat.id]['name']}',"
                                               f"'{user_triger[update.effective_chat.id]['link']}',"
                                               f"'{categories_pd.loc[int(update.message.text) - 1,'name']}');")
                                user_triger[update.effective_chat.id]['step'] = 0
                                context.bot.send_message(chat_id=update.effective_chat.id, text="Продукт добавлен.\nЧто бы добавить ещё, просто впишите название продукта.",
                             reply_markup=ReplyKeyboardMarkup([['Прекратить ввод']], resize_keyboard=True,
                                                              one_time_keyboard=False))
                            else:
                                context.bot.send_message(chat_id=update.effective_chat.id, text="Такого номера нет! Выберите повторно из списка. К какой категории относится товар?")
                        else:
                            context.bot.send_message(chat_id=update.effective_chat.id, text="Введите номер категории цифрами, чтобы выбрать из списка.")
                            return
                elif user_triger[update.effective_chat.id]['Delete'] and user_triger[update.effective_chat.id]['categories'] != "None":
                    products_pd = pd.read_sql_query(f"SELECT name, link FROM products WHERE categories = '{user_triger[update.effective_chat.id]['categories']}';",engine)
                    if update.message.text.isnumeric():
                        if int(update.message.text) <= len(products_pd) and int(update.message.text) > 0:
                            user_triger[update.effective_chat.id]['Delete'] = False
                            engine.execute(f"DELETE FROM products WHERE link = '{str(products_pd.loc[int(update.message.text)-1,'link']).replace('%','%%')}';")
                            context.bot.send_message(chat_id=update.effective_chat.id, text="Продукт удален.")
                            globals()[triger](update, context, user_triger)
                elif user_triger[update.effective_chat.id]['Edit_link'] and user_triger[update.effective_chat.id]['categories'] != "None":
                    if user_triger[update.effective_chat.id]['step'] == 0:
                        products_pd = pd.read_sql_query(f"SELECT name, link FROM products WHERE categories = '{user_triger[update.effective_chat.id]['categories']}';", engine)
                        user_triger[update.effective_chat.id]['step'] = 1
                        if update.message.text.isnumeric():
                            user_triger[update.effective_chat.id]['name'] = str(products_pd.loc[int(update.message.text) - 1, 'name']).replace('%','%%')
                            user_triger[update.effective_chat.id]['link'] = str(products_pd.loc[int(update.message.text) - 1, 'link']).replace('%','%%')
                            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Введите новую ссылку на продукта с названием \"{user_triger[update.effective_chat.id]['name']}\".")
                        else:
                            context.bot.send_message(chat_id=update.effective_chat.id, text="Введите номер продукта цифрами, чтобы выбрать из списка.")
                    elif user_triger[update.effective_chat.id]['step'] == 1:
                        engine.execute(f"UPDATE products SET link = '{str(update.message.text).replace('%','%%')}' WHERE link = '{user_triger[update.effective_chat.id]['link']}' and name = '{user_triger[update.effective_chat.id]['name']}';")
                        context.bot.send_message(chat_id=update.effective_chat.id, text="Новую ссылку на продукт запомнил.")
                        globals()[triger](update, context, user_triger)
    # Все дествия с категориями
    elif triger == 'categories':
        categories_pd = pd.read_sql_query("SELECT name FROM categories ORDER BY name ASC;", engine)
        if 'вернуться в меню "еда"' == update.message.text.lower():
            eat(update, context, user_triger)
        if 'отменить' == update.message.text.lower() or 'отмена' == update.message.text.lower() or 'прекратить ввод' == update.message.text.lower():
            globals()[triger](update, context, user_triger)
        elif "добавить новую категорию" == update.message.text.lower():
            user_triger[update.effective_chat.id]['New'] = True
            user_triger[update.effective_chat.id]['Delete'] = False
            context.bot.send_message(chat_id=update.effective_chat.id, text="Введите название категории",
                             reply_markup=ReplyKeyboardMarkup([['Отменить']], resize_keyboard=True,
                                                              one_time_keyboard=False))
        elif "удалить категорию" == update.message.text.lower() or "посмотреть категории" == update.message.text.lower():
            if len(categories_pd) != 0:
                if "удалить категорию" == update.message.text.lower():
                    user_triger[update.effective_chat.id]['New'] = False
                    user_triger[update.effective_chat.id]['Delete'] = True
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Введите номер категории, цифрами, чтобы удалить.",
                             reply_markup=ReplyKeyboardMarkup([['Отменить']], resize_keyboard=True,
                                                              one_time_keyboard=False))
                text=''
                for i in range(len(categories_pd)):
                    text += f'{i+1}) {categories_pd.loc[i,"name"]}\n'
                context.bot.send_message(chat_id=update.effective_chat.id, text=text)
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Категорий нет.")
        else:
            if user_triger[update.effective_chat.id]['New'] or user_triger[update.effective_chat.id]['Delete']:
                if user_triger[update.effective_chat.id]['New']:
                    engine.execute(f"INSERT INTO categories(name) VALUES('{update.message.text}');")  # добавляет в список
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Новая категория добавлена.\nЧто бы добавить еще категорию, просто впишите её название.",
                             reply_markup=ReplyKeyboardMarkup([['Прекратить ввод']], resize_keyboard=True,
                                                              one_time_keyboard=False))
                elif user_triger[update.effective_chat.id]['Delete']:
                    if update.message.text.isnumeric():
                        if int(update.message.text) <= len(categories_pd) and int(update.message.text) > 0:
                            remember = categories_pd.loc[int(update.message.text)-1, 'name']
                            engine.execute(f"DELETE FROM categories WHERE name = '{remember}';")
                            user_triger[update.effective_chat.id]['Delete'] = False
                            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Категория {remember} удалена.")
                            globals()[triger](update, context, user_triger)
                        else:
                            context.bot.send_message(chat_id=update.effective_chat.id, text="Введите номер категории, чтобы удалить. Такого номера нет!")
                    else:
                        context.bot.send_message(chat_id=update.effective_chat.id, text="Введите номер категории цифрами, чтобы удалить.")
    # Все дествия с частатой заказа
    elif triger == 'frequency':
        categories_pd = pd.read_sql_query("SELECT name, frequency FROM categories ORDER BY name ASC;", engine)
        if 'вернуться в меню "еда"' == update.message.text.lower():
            eat(update, context, user_triger)
        elif 'отменить' == update.message.text.lower() or 'отмена' == update.message.text.lower():
            globals()[triger](update, context, user_triger)
        elif 'изменить' == update.message.text.lower() or 'проверить' == update.message.text.lower():
            if 'изменить' == update.message.text.lower():
                # context.bot.send_message(chat_id=update.effective_chat.id, text=text + "Введите новое количество дней.")
                user_triger[update.effective_chat.id]['Edit'] = True
                """изменяем показания"""
            elif 'проверить' == update.message.text.lower():
                user_triger[update.effective_chat.id]['Edit'] = False
                # context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=ReplyKeyboardMarkup([['Отменить']], resize_keyboard=True, one_time_keyboard=False))
                """предлогаем изменить показания и посмотреть другой продукт в этой категории или в другой"""
           #### Если снова нужно будет сделать переодичность на категории и продукты ту ужалить эту часть ####
            user_triger[update.effective_chat.id]['edit_products'] = False
            if user_triger[update.effective_chat.id]['Edit']:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="Выберите категорию.Введите номер категории, цифрами.",
                                         reply_markup=ReplyKeyboardMarkup([['Отменить']], resize_keyboard=True,
                                                                          one_time_keyboard=False))
            text = ''
            for i in range(len(categories_pd)):
                text += f'{i + 1}) {categories_pd.loc[i, "name"]} - 1 раз в {categories_pd.loc[i, "frequency"]}дн.\n'
            context.bot.send_message(chat_id=update.effective_chat.id, text=text)
            if user_triger[update.effective_chat.id]['Edit'] == False:
                globals()[triger](update, context, user_triger)
            #### Если снова нужно будет сделать переодичность на категории и продукты ту ужалить эту часть  и раскоментировать часть ниже####
            # context.bot.send_message(chat_id=update.effective_chat.id, text=f"Что желаете {update.message.text.lower()}? Периодичность заказа продуктов или категорий?", reply_markup=ReplyKeyboardMarkup([['продуктов', 'категорий'], ['Вернуться в меню "Еда"']], resize_keyboard=True, one_time_keyboard=False))
        # elif 'продуктов' == update.message.text.lower():
        #     user_triger[update.effective_chat.id]['edit_products'] = True
        #     if user_triger[update.effective_chat.id]['step'] == 0:
        #         user_triger[update.effective_chat.id]['step'] = 1
        #         context.bot.send_message(chat_id=update.effective_chat.id,
        #                                  text="Выберите категорию.Введите номер категории, цифрами.",
        #                                  reply_markup=ReplyKeyboardMarkup([['Отменить']], resize_keyboard=True,
        #                                                                   one_time_keyboard=False))
        #         text = ''
        #         for i in range(len(categories_pd)):
        #             text += f'{i + 1}) {categories_pd.loc[i, "name"]}\n'
        #         context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        # elif 'категорий' == update.message.text.lower():
        #     user_triger[update.effective_chat.id]['edit_products'] = False
        #     if user_triger[update.effective_chat.id]['Edit']:
        #         context.bot.send_message(chat_id=update.effective_chat.id,
        #                                  text="Выберите категорию.Введите номер категории, цифрами.",
        #                                  reply_markup=ReplyKeyboardMarkup([['Отменить']], resize_keyboard=True,
        #                                                                   one_time_keyboard=False))
        #     text = ''
        #     for i in range(len(categories_pd)):
        #         text += f'{i + 1}) {categories_pd.loc[i, "name"]} - 1 раз в {categories_pd.loc[i, "frequency"]}дн.\n'
        #     context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        #     if user_triger[update.effective_chat.id]['Edit'] == False:
        #         globals()[triger](update, context, user_triger)
        elif user_triger[update.effective_chat.id]['edit_products']:
            if user_triger[update.effective_chat.id]['step'] == 1:
                if update.message.text.isnumeric():
                    if int(update.message.text) <= len(categories_pd) and int(update.message.text) > 0:
                        user_triger[update.effective_chat.id]['step'] = 2
                        user_triger[update.effective_chat.id]['categories'] = str(categories_pd.loc[int(update.message.text)-1,'name'])
                        info = pd.read_sql(f"SELECT name, link, frequency FROM products WHERE categories = '{user_triger[update.effective_chat.id]['categories']}' ORDER BY name ASC;",engine)
                        if len(info) != 0:
                            text = ''
                            for i in range(len(info)):
                                text += f'{i + 1}) {info.loc[i, "name"]} - 1 раз в {info.loc[i, "frequency"]}дн.\n'
                            context.bot.send_message(chat_id=update.effective_chat.id, text=text)
                        if user_triger[update.effective_chat.id]['Edit']:
                            context.bot.send_message(chat_id=update.effective_chat.id,
                                                     text="Выберите продукт для изменения периодичности заказа. Введите номер продукта, цифрами.",
                                                     reply_markup=ReplyKeyboardMarkup([['Отменить']],
                                                                                      resize_keyboard=True,
                                                                                      one_time_keyboard=False))
                        else:
                            globals()[triger](update, context, user_triger)
                    else:
                        context.bot.send_message(chat_id=update.effective_chat.id, text="Введите номер категории, чтобы выбрать. Такого номера нет!")
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Введите номер категории цифрами, чтобы выбрать.")
            elif user_triger[update.effective_chat.id]['step'] == 2 and user_triger[update.effective_chat.id]['Edit']:
                if update.message.text.isnumeric():
                    info = pd.read_sql(f"SELECT name, link, frequency FROM products WHERE categories = '{user_triger[update.effective_chat.id]['categories']}' ORDER BY name ASC;", engine)
                    if int(update.message.text) <= len(info) and int(update.message.text) > 0:
                        user_triger[update.effective_chat.id]['step'] = 3
                        user_triger[update.effective_chat.id]['link'] = str(info.loc[int(update.message.text) - 1, 'link'])
                        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Периодичность заказа данного продукта 1 раз в {info.loc[int(update.message.text) - 1, 'frequency']} дн.\n Введите новое значение.")
                    else:
                        context.bot.send_message(chat_id=update.effective_chat.id,
                                                 text="Введите номер продукта, чтобы выбрать. Такого номера нет!")
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text="Введите номер продукта цифрами, чтобы выбрать.")
            elif user_triger[update.effective_chat.id]['step'] == 3 and user_triger[update.effective_chat.id]['Edit']:
                if ',' in update.message.text:
                    frequency = str(update.message.text).replace(',', '.')
                else:
                    frequency = update.message.text

                engine.execute(f"UPDATE products SET frequency = '{frequency}' WHERE link = '{user_triger[update.effective_chat.id]['link']}';")
                context.bot.send_message(chat_id=update.effective_chat.id, text="Готово, запомнил.")
                globals()[triger](update, context, user_triger)
        elif user_triger[update.effective_chat.id]['Edit'] and user_triger[update.effective_chat.id]['edit_products'] == False:
            if user_triger[update.effective_chat.id]['step'] == 0:
                if update.message.text.isnumeric():
                    if int(update.message.text) <= len(categories_pd) and int(update.message.text) > 0:
                        user_triger[update.effective_chat.id]['step'] = 1
                        user_triger[update.effective_chat.id]['name'] = str(
                            categories_pd.loc[int(update.message.text) - 1, 'name'])
                        context.bot.send_message(chat_id=update.effective_chat.id,
                                                 text=f"Периодичность заказа из данной катигории 1 раз в {categories_pd.loc[int(update.message.text) - 1, 'frequency']} дн.\n Введите новое значение.")
                    else:
                        context.bot.send_message(chat_id=update.effective_chat.id,
                                                 text="Введите номер продукта, чтобы выбрать. Такого номера нет!")
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text="Введите номер продукта цифрами, чтобы выбрать.")
            elif user_triger[update.effective_chat.id]['step'] == 1:
                if ',' in update.message.text:
                    frequency = str(update.message.text).replace(',', '.')
                else:
                    frequency = update.message.text
                engine.execute(f"UPDATE categories SET frequency = '{frequency}' WHERE name = '{user_triger[update.effective_chat.id]['name']}';")
                context.bot.send_message(chat_id=update.effective_chat.id, text="Готово, запомнил.")
                globals()[triger](update, context, user_triger)
    elif triger == 'query_for_buy_next':
        info = pd.read_sql(f"SELECT name FROM user_family WHERE user_id = '{update.effective_chat.id}';",engine)
        check_info = pd.read_sql(f"SELECT quantity FROM shopping_list WHERE products = '{str(user_triger[update.effective_chat.id]['products_name']).replace('%','%%')}' AND order_date = '{str(datetime.now().strftime('%d.%m.%Y'))}' ORDER BY quantity DESC LIMIT 1;", engine)
        not_double = True
        if update.message.text.isnumeric():
            if len(check_info) != 0:
                if int(update.message.text) <= int(check_info.loc[0, "quantity"]):#max_check_info_quantity:
                    not_double = False
                    check_info_name = pd.read_sql(f"SELECT name FROM shopping_list WHERE products = '{str(user_triger[update.effective_chat.id]['products_name']).replace('%', '%%')}' AND quantity = '{check_info.loc[0, 'quantity']}' AND order_date = '{str(datetime.now().strftime('%d.%m.%Y'))}';",engine)
                    if check_info_name.loc[0, 'name'] == "Андрей":
                        str_and = 'и '
                        install = 'установил'
                    elif "для блюда" in check_info_name.loc[0, 'name']:
                        str_and = ''
                        install = ', установленно'
                    else:
                        str_and = 'и '
                        install = 'установила'
                    user(update, context, f"Данный продукт уже был выбран {str_and}{check_info_name.loc[0, 'name']} {install} {check_info.loc[0, 'quantity']}шт.")
            if not_double:
                engine.execute(f"INSERT INTO shopping_list(categories, products, quantity, name, order_date) "
                               f"VALUES('{user_triger[update.effective_chat.id]['categories']}',"
                               f"'{str(user_triger[update.effective_chat.id]['products_name']).replace('%','%%')}',"
                               f"'{update.message.text}','{info.loc[0, 'name']}',"
                               f"'{str(datetime.now().strftime('%d.%m.%Y'))}');")
                user(update, context, "Добавил в список покупок.")
            user_triger.pop(update.effective_chat.id)
        else:
            if 'отменить ввод' == update.message.text.lower():
                user(update, context, "Отмена, действий. Возвращаемся в главное меню.")
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Введите количество продукта цифрами.")
    elif triger == 'dish':
        if 'вернуться в меню "еда"' == update.message.text.lower():
            eat(update, context, user_triger)
        elif 'отменить' == update.message.text.lower() or 'отмена' == update.message.text.lower():
            globals()[triger](update, context, user_triger)
        elif 'Создать набор для блюда' == update.message.text:
            user_triger[update.effective_chat.id]['create'] = True
            context.bot.send_message(chat_id=update.effective_chat.id,text='Введите названия блюда.',
                             reply_markup=ReplyKeyboardMarkup([['Отменить']], resize_keyboard=True,
                                                              one_time_keyboard=False))
        elif 'Добавить набор в корзину' == update.message.text:
            user_triger[update.effective_chat.id]['create'] = False
            dish_pd = pd.read_sql(f"SELECT * FROM dish;", engine)
            keyboard = []
            for j in range(len(dish_pd)):
                print(j)
                keyboard += [[InlineKeyboardButton(dish_pd.loc[j, 'name'], callback_data='dish_add-' + str(dish_pd.loc[j, 'id']))]]
            if len(keyboard) > 0:
                sms = "Для какого блюда добавим продукты в корзину?"
                context.bot.send_message(chat_id=update.effective_chat.id, text=sms,
                                         reply_markup=InlineKeyboardMarkup(keyboard))
            #######################################################
        elif user_triger[update.effective_chat.id]['create']:
            if user_triger[update.effective_chat.id]['step'] == 0:
                user_triger[update.effective_chat.id]['name'] = update.message.text
                context.bot.send_message(chat_id=update.effective_chat.id, text='Сколько по времени занимает приготовление блюда?',
                                         reply_markup=ReplyKeyboardMarkup([['Отменить']], resize_keyboard=True,
                                                                          one_time_keyboard=False))
                user_triger[update.effective_chat.id]['step'] = 1
            elif user_triger[update.effective_chat.id]['step'] == 1:

                user_triger[update.effective_chat.id]['cooking_time'] = update.message.text
                context.bot.send_message(chat_id=update.effective_chat.id, text='Сколько человек необходимо для приготовления данного блюда?',
                                         reply_markup=ReplyKeyboardMarkup([['Отменить']], resize_keyboard=True,
                                                                          one_time_keyboard=False))
                user_triger[update.effective_chat.id]['step'] = 2

            elif user_triger[update.effective_chat.id]['step'] == 2:
                if update.message.text.isnumeric():
                    user_triger[update.effective_chat.id]['num_need_people'] = update.message.text
                    categories = pd.read_sql(f"SELECT * FROM categories;", engine)
                    keyboard = []
                    for j in range(len(categories)):
                        keyboard += [[InlineKeyboardButton(categories.loc[j, 'name'], callback_data='dish_choice_categories-' + str(categories.loc[j, 'name']))]]
                    if len(keyboard) > 1:
                        sms = "Что из данных категорий необходимо приобрести для приготовления данного блюда?"
                        context.bot.send_message(chat_id=update.effective_chat.id, text=sms, reply_markup=InlineKeyboardMarkup(keyboard))
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Обычно, количество вводят цифрами. Попробуйте еще раз.")
        elif 'Добавить рецепт' == update.message.text or 'Посмотреть рецепт' == update.message.text or 'Удалить рецепт' == update.message.text or 'Удалить блюдо' == update.message.text or 'Посмотреть набор для блюда' == update.message.text:
            info = pd.read_sql("SELECT * FROM dish ORDER BY id ASC;", engine)
            if len(info) != 0:
                text = ''
                for i in range(len(info)):
                    text += f'{i + 1}) {info.loc[i, "name"]}\n'
                if 'Добавить рецепт' == update.message.text:
                    user_triger[update.effective_chat.id]['add_note'] = True
                    user_triger[update.effective_chat.id]['show_note'] = False
                    user_triger[update.effective_chat.id]['show_product'] = False
                    user_triger[update.effective_chat.id]['delete'] = 'None'
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Выберете блюдо для которого добавим новый рецепт(или заменим на новый).\n"+text)
                elif 'Посмотреть рецепт' == update.message.text:
                    user_triger[update.effective_chat.id]['add_note'] = False
                    user_triger[update.effective_chat.id]['show_note'] = True
                    user_triger[update.effective_chat.id]['show_product'] = False
                    user_triger[update.effective_chat.id]['delete'] = 'None'
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Выберете блюдо для которого нужен рецепт.\n"+text)
                elif 'Удалить рецепт' == update.message.text:
                    user_triger[update.effective_chat.id]['add_note'] = False
                    user_triger[update.effective_chat.id]['show_note'] = False
                    user_triger[update.effective_chat.id]['show_product'] = False
                    user_triger[update.effective_chat.id]['delete'] = 'рецепт'
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Выберете блюдо рецепт которого нужно удалить.\n"+text)
                elif 'Удалить блюдо' == update.message.text:
                    user_triger[update.effective_chat.id]['add_note'] = False
                    user_triger[update.effective_chat.id]['show_note'] = False
                    user_triger[update.effective_chat.id]['show_product'] = False
                    user_triger[update.effective_chat.id]['delete'] = 'блюдо'
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Выберете блюдо которое нужно удалить.\n"+text)
                elif 'Посмотреть набор для блюда' == update.message.text:
                    user_triger[update.effective_chat.id]['add_note'] = False
                    user_triger[update.effective_chat.id]['show_note'] = False
                    user_triger[update.effective_chat.id]['show_product'] = True
                    user_triger[update.effective_chat.id]['delete'] = 'None'
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Выберете блюдо, для того чтобы посмотреть необходимый список продуктов.\n"+text)
        elif user_triger[update.effective_chat.id]['add_note']:
            if user_triger[update.effective_chat.id]['step'] == 0:
                info = pd.read_sql("SELECT * FROM dish ORDER BY id ASC;", engine)
                if update.message.text.isnumeric():
                    if int(update.message.text) <= len(info):
                        user_triger[update.effective_chat.id]['step'] = 1
                        i = int(update.message.text) - 1
                        user_triger[update.effective_chat.id]['name'] = info.loc[i,'name']
                        context.bot.send_message(chat_id=update.effective_chat.id, text="Напишите рецепт и я его запомню.")
                    else:
                        context.bot.send_message(chat_id=update.effective_chat.id, text="Введите номер блюда, чтобы выбрать. Такого номера нет!")
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Введите номер блюда цифрами, чтобы выбрать.")
            elif user_triger[update.effective_chat.id]['step'] == 1:
                engine.execute(f"UPDATE dish SET note = '{update.message.text}' WHERE name = '{user_triger[update.effective_chat.id]['name']}';")
                context.bot.send_message(chat_id=update.effective_chat.id, text="Отлично, записал!")
                user_triger.pop(update.effective_chat.id)
                user_triger[update.effective_chat.id] = {
                    'triger': "dish",
                    'create': False,
                    'add_note': False,
                    'show_note': False,
                    'show_product': False,
                    'delete': 'None',
                    'name': 'None',
                    'num_need_people': 1,
                    'coocing_time': 0,
                    'step': 0,
                    'list_products': []
                }
        elif user_triger[update.effective_chat.id]['show_note']:
            info = pd.read_sql("SELECT * FROM dish ORDER BY id ASC;", engine)
            if update.message.text.isnumeric():
                if int(update.message.text) <= len(info):
                    i = int(update.message.text) - 1
                    if info.loc[i, 'note'] is not None:
                        context.bot.send_message(chat_id=update.effective_chat.id, text=f"\"{info.loc[i,'name']}\":\n{info.loc[i,'note']}")
                    else:
                        context.bot.send_message(chat_id=update.effective_chat.id, text=f"\"{info.loc[i, 'name']}\". Рецепт не добавлен.")
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Введите номер блюда, чтобы выбрать. Такого номера нет!")
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Введите номер блюда цифрами, чтобы выбрать.")
        elif user_triger[update.effective_chat.id]['delete'] != 'None':
            info = pd.read_sql("SELECT * FROM dish ORDER BY id ASC;", engine)
            if update.message.text.isnumeric():
                if int(update.message.text) <= len(info):
                    i = int(update.message.text) - 1
                    if user_triger[update.effective_chat.id]['delete'] == 'рецепт':
                        engine.execute(f"UPDATE dish SET note = 'Рецепта нет.' WHERE name = '{info.loc[i, 'name']}';")
                        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Рецепт блюда \"{info.loc[i, 'name']}\" успешно удалён.")
                    elif user_triger[update.effective_chat.id]['delete'] == 'блюдо':
                        engine.execute(f"DELETE FROM dish WHERE name = '{info.loc[i, 'name']}';")
                        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Блюдо \"{info.loc[i, 'name']}\" успешно удалено.")
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Введите номер блюда. Такого номера нет!")
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Введите номер блюда цифрами.")
        elif user_triger[update.effective_chat.id]['show_product']:
            info = pd.read_sql("SELECT * FROM dish ORDER BY id ASC;", engine)
            if update.message.text.isnumeric():
                if int(update.message.text) <= len(info):
                    i = int(update.message.text) - 1
                    list_name_product = ''
                    for id_product in str(info.loc[i, 'list_product']).split(','):
                        product_db = pd.read_sql(f"SELECT name FROM products WHERE id = {id_product};", engine)
                        list_name_product += "• " + str(product_db.loc[0, 'name']) + '\n'
                    sms = f"Название блюда: {info.loc[i, 'name']}\n" \
                          f"Необходимые продукты для приготовления:\n{list_name_product}"
                    context.bot.send_message(chat_id=update.effective_chat.id, text=sms)
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text="Введите номер блюда. Такого номера нет!")
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Введите номер блюда цифрами.")

    elif triger == 'dish_like':
        if update.message.text.isnumeric():
            engine.execute(f"UPDATE dish SET like_dish = '{int(update.message.text)}' WHERE id = '{user_triger[update.effective_chat.id]['id']}'")
            context.bot.send_message(chat_id=update.effective_chat.id, text="Отлично, запомнил.")
            user_triger.pop(update.effective_chat.id)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Введите количество лайков для блюда цифрами.")