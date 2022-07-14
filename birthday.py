# coding=UTF-8
#
#
import pandas as pd
import logging
import telegram

from datetime import datetime, timedelta
from work import TELEGRAM_TOKEN, ivea_family, papa, mama, kids
from sqlalchemy import create_engine

working_folder = '/home/menace134/py/family/'

logging.basicConfig(filename=working_folder + 'birthday.log',
                     filemode='a',
                     level=logging.INFO,
                     format='%(asctime)s %(process)d-%(levelname)s %(message)s',
                     datefmt='%d-%b-%y %H:%M:%S')

bot = telegram.Bot(TELEGRAM_TOKEN)

engine = create_engine(ivea_family)  # данные для соединия с сервером

def finder():
    birthday_list = "В этом месяце дни рождения у следующих людей:\n"
    now = datetime.now()
    time = datetime(now.year, now.month, now.day).strftime('%m-%d')# now
    time2 = (now + timedelta(days=+1)).strftime('%m-%d')# +1 day
    time3 = (now + timedelta(days=+7)).strftime('%m-%d')# +7 day
    info = pd.read_sql(f"SELECT * FROM birthday", engine)# WHERE day ='{time}' or day ='{time2}' or day ='{time3}')
    for i in range(len(info)):
        text=''
        age=int(now.strftime('%Y'))-int(info.loc[i, "day"].strftime('%Y')) #узнаем сколько лет исполняется
        num = str(age)[len(str(age)) - 1:]
        if age >= 11 and age <=19:
            Y = 'лет.'
        elif int(num) == 1:
            Y = 'год.'
        elif int(num) >= 2 and int(num) <= 4:
            Y = 'года.'
        elif int(num) == 5 or int(num) == 0:
            Y = 'лет. ЮБИЛЕЙ!'
        elif int(num) >= 5:
            Y = 'лет.'
        if int(now.strftime('%d')) == 1: #срабатывает каждый первый день месяца и отправляет лист
            if int(info.loc[i, "day"].strftime('%m')) == int(now.strftime('%m')):
                birthday_list += f"{str(info.loc[i, 'day'].strftime('%d.%m'))} у {str(info.loc[i, 'name'])}, исполняется {age} {Y}\n"
        if info.loc[i, "day"].strftime('%m-%d') == time:
            text=f"🎊🎉🎂 Сегодня день рождения у {info.loc[i,'name']}, исполняется {str(age)} {Y}🎂🎉🎊"
            logging.info(f"сегодня день рождения у {info.loc[i, 'name']}, исполняется {age} {Y}")
        elif info.loc[i, "day"].strftime('%m-%d') == time2:
            text=f"🎂 Завтра день рождения у {info.loc[i, 'name']}, исполняется {age} {Y} 🎂"
            logging.info(f"Завтра день рождения у {info.loc[i, 'name']}, исполняется {age} {Y}")
        elif info.loc[i, "day"].strftime('%m-%d') == time3:
            text=f"🎂 Через неделю день рождения у {info.loc[i, 'name']}, исполняется {age} {Y} 🎂"
            logging.info(f"через неделю исполнится у {info.loc[i, 'name']}, исполняется {age} {Y}")
        if text != '':
            send = info.loc[i, "send"].split(',')
            logging.info(send)
            for name in send:
                user_id = pd.read_sql(f"SELECT user_id FROM user_family WHERE name ='{name}'", engine)
                try:
                    logging.info(f'chat_id={str(user_id.loc[0, "user_id"])} - "{name}", text={text}))')
                    bot.send_message(chat_id=int(user_id.loc[0, "user_id"]), text=text)
                except Exception as err:
                    logging.info(f'chat_id={str(user_id.loc[0, "user_id"])} - "{name}" - не отправил\n{err}')
    if birthday_list != "В этом месяце дни рождения у следующих людей:\n":
        logging.info(birthday_list)
        bot.send_message(chat_id=papa, text=birthday_list)

finder()