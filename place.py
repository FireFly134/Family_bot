# coding=UTF-8
#
#

import logging
from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy import create_engine

from work import ivea_family, kids, working_folder

logging.basicConfig(filename=working_folder + 'log/place.log',
                    filemode='a',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%d.%m.%Y %H:%M:%S')

engine = create_engine(ivea_family)  # данные для соединия с сервером
def new_month():
    kids = ['Амира', 'Лиза', 'Лейла', 'Вова']
    for name_kid in kids:
        info = pd.read_sql(f"SELECT mark, antimark, star, poo, iq, brain, books_end FROM user_family WHERE name = '{name_kid}'",
                           engine)
        month = int(
            datetime.now().strftime('%m')) - 1  # от текущего месяца отнимаем 1 чтобы узнать предыдущий и записать его.
        year = int(datetime.now().strftime('%Y'))  # так же узнаем год.
        if month == 0:  # месяца 0 не бывает делаем поправки и понимаем что это было декабрь прошлого года
            month = 12
            year -= 1
            # Сохраняем всю эту хрень и обнуляем позиции для нового месяца
        engine.execute(f"INSERT INTO statistics(name, month, year, mark, antimark, star, poo, iq, brain, books_end) VALUES('{name_kid}','{month}','{year}','{info.loc[0, 'mark']}','{info.loc[0, 'antimark']}','{info.loc[0, 'star']}','{info.loc[0, 'poo']}','{info.loc[0, 'iq']}','{info.loc[0, 'brain']}','{info.loc[0, 'books_end']}');")
        if info.loc[0, 'mark'] < 0:
            engine.execute(f"UPDATE user_family SET mark = 0, star = 0, antimark = 0, anti_every_day = 0, poo = 0, brain = 0, books_end = 0  WHERE name = '{name_kid}';")
        else:
            engine.execute(f"UPDATE user_family SET star = 0, antimark = 0, anti_every_day = 0, poo = 0, brain = 0, books_end = 0  WHERE name = '{name_kid}';")
        logging.info(f"new_month({name_kid})")
def place():
    month = int(datetime.now().strftime('%m')) - 1
    year = int(datetime.now().strftime('%Y'))
    if month == 0:
        month = 12
        year -= 1
    info = pd.read_sql(
        f"SELECT name, mark, star, brain, iq FROM statistics WHERE month = '{month}' and year = '{year}';", engine)
    statistic = {}
    for i in range(len(info)):
        like = int(info.loc[i, "mark"])
        star = int(info.loc[i, "star"])
        brain = int(info.loc[i, "brain"])
        iq = int(info.loc[i, "iq"])
        result = (like + (star * 100)) + ((brain * 25) + (iq / 2))
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
if __name__ == "__main__":
    print(__name__)
    print('Создаем статистику')
    new_month()
    print('Выставляем места')
    place()