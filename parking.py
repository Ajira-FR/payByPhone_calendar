# coding: utf-8

import logging
from logging.handlers import RotatingFileHandler
import time
import requests
import bs4
import re
import sqlite3
from datetime import datetime
from config import Config

ARG1 = {
    'ctl00$ContentPlaceHolder1$CallingCodeDropDownList': '-3',
     'ctl00$ContentPlaceHolder1$AccountTextBox': Config.PHONE_NUMBER,
     'ctl00$ContentPlaceHolder1$PinOrLast4DigitCcTextBox': Config.PIN,
     'ctl00$ContentPlaceHolder1$RememberPinCheckBox': 'on',
     'ctl00$ContentPlaceHolder1$LoginButton': 'se connecter'
}

ARG2 = {
    '__EVENTTARGET': '',
    '__EVENTARGUMENT': '',
    'ctl00$ContentPlaceHolder1$LocationNumberTextBox': Config.PARKING_CODE,
    'ctl00$ContentPlaceHolder1$NextButton': 'suivant'
}

ARG3 = {
    '__EVENTTARGET': '',
    '__EVENTARGUMENT': '',
    'ctl00$ContentPlaceHolder1$SelectVehicleDropDownList': Config.CAR_ID,
    'ctl00$ContentPlaceHolder1$DurationTextBox': '1',
    'ctl00$ContentPlaceHolder1$TimeUnitDropDownList': '3',
    'ctl00$ContentPlaceHolder1$NextButton': 'suivant'
}

ARG4 = {
    '__EVENTTARGET': '',
    '__EVENTARGUMENT': '',
    'ctl00$ContentPlaceHolder1$ConfirmParking': 'confirmer le stationnement',
    'ctl00$ContentPlaceHolder1$NoRatesFoundErrorHidden': 'false',
    'ctl00$ContentPlaceHolder1$SessionQuoteErrorHidden': 'false',
    'ctl00$ContentPlaceHolder1$ParkingSessionValidationErrorHidden': 'false'
}

HEADERS = {
    'Origin': 'https://m.paybyphone.fr',
    'Referer': Config.URL,
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36'
}

REGEXP1 = "(\\d+)\\s+jours?"
REGEXP2 = "(\\d+)\\s+heures?"
REGEXP3 = "(\\d+)\\s+mins?"

PATTERN1 = re.compile(REGEXP1)
PATTERN2 = re.compile(REGEXP2)
PATTERN3 = re.compile(REGEXP3)

def findToken(page):
    html = bs4.BeautifulSoup(page, "html.parser").find("form", attrs={"id":"aspnetForm"})

    wiewstate = html.find("input", attrs={"id":"__VIEWSTATE"})["value"]
    wiewstategnerator = html.find("input", attrs={"id":"__VIEWSTATEGENERATOR"})["value"]
    eventvalidation = html.find("input", attrs={"id":"__EVENTVALIDATION"})["value"]

    return wiewstate, wiewstategnerator, eventvalidation

def connection(logger):
    logger.info("Try to connect ...")
    s = requests.session()
    req = s.get(Config.URL)

    a, b, c = findToken(req.text)
    ARG1['__VIEWSTATE'] = a
    logger.info("__VIEWSTATE {}".format(a[:10]))
    ARG1['__VIEWSTATEGENERATOR'] = b
    logger.info("__VIEWSTATEGENERATOR {}".format(b[:10]))
    ARG1['__EVENTVALIDATION'] = c
    logger.info("__EVENTVALIDATION {}".format(c[:10]))

    req = s.post(Config.URL, data=ARG1, allow_redirects=True)
    logger.info("Connection success !")
    return req, s


def remainingTime(request, session, logger):
    logger.info("Try to know remaining time ...")
    html = bs4.BeautifulSoup(request.text, "html.parser")
    page = html.find("span", attrs={"id":"ctl00_ContentPlaceHolder1_ActiveParkingGridView_ctl02_TimeLeftLabel"})
    logger.info("Span contains {}".format(page))

    if page:
        days = PATTERN1.search(page.text)
        if days:
            days = int(days.group(1))
        else:
            days = 0
        logger.info("Days = {}".format(days))
        hours = PATTERN2.search(page.text)
        if hours:
            hours = int(hours.group(1))
        else:
            hours = 0
        logger.info("Hours = {}".format(hours))
        minutes = PATTERN3.search(page.text)
        if minutes:
            minutes = int(minutes.group(1))
        else:
            minutes = 0
        logger.info("Minutes = {}".format(minutes))
        return (days, hours, minutes)
    else:
        return None

def newParking(nbDays, request, session, logger):
    logger.info("Try to get a new parking ticket ...")
    a, b, c = findToken(request.text)
    ARG2['__VIEWSTATE'] = a
    ARG2['__VIEWSTATEGENERATOR'] = b
    ARG2['__EVENTVALIDATION'] = c

    req = session.post(request.url, data=ARG2, allow_redirects=True)
    logger.info("RCZ found !")

    a, b, c = findToken(req.text)
    ARG3["ctl00$ContentPlaceHolder1$DurationTextBox"] = nbDays
    ARG3['__VIEWSTATE'] = a
    ARG3['__VIEWSTATEGENERATOR'] = b
    ARG3['__EVENTVALIDATION'] = c

    req = session.post(req.url, data=ARG3, allow_redirects=True)
    logger.info("Choose a {} day(s) tickets".format(nbDays))

    a, b, c = findToken(req.text)
    ARG4['__VIEWSTATE'] = a
    ARG4['__VIEWSTATEGENERATOR'] = b
    ARG4['__EVENTVALIDATION'] = c

    req = session.post(req.url, data=ARG4, allow_redirects=True)

    html = bs4.BeautifulSoup(req.text, "html.parser")
    result = html.find("span", attrs={"id":"ctl00_ContentPlaceHolder1_MessageBoxTable_MessageLabel"})

    if result:
        #maybe 'é' result as an error (confirmé)
        if "Stationnement confirm" in result.string:
            logger.info("Parking confirmed !")
        else:
            logger.warning("Strange ! span contains : {}".format(result))
    else:
        logger.error(req.text)

def todayCalendar(request, session, logger, database):
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    today = datetime.today()
    today = datetime(today.year, today.month, today.day)
    timestamp = time.mktime(today.timetuple())
    try:
        cur.execute("SELECT * FROM parking WHERE timestamp = ?", (timestamp,))
        res = cur.fetchone()
        cur.close()
        if res:
            logger.info("SQL = {}".format(res))
            return True
        else:
            return False

    except sqlite3.Error as e:
        logger.error(e.args[0])
        cur.close()

if __name__ == "__main__":
    # création de l'objet logger qui va nous servir à écrire dans les logs
    logger = logging.getLogger()
    # on met le niveau du logger à DEBUG, comme ça il écrit tout
    logger.setLevel(logging.DEBUG)

    # création d'un formateur qui va ajouter le temps, le niveau
    # de chaque message quand on écrira un message dans le log
    formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
    # création d'un handler qui va rediriger une écriture du log vers
    # un fichier en mode 'append', avec 1 backup et une taille max de 1Mo
    file_handler = RotatingFileHandler(Config.LOGGER, 'a', 1000000, 1)
    # on lui met le niveau sur DEBUG, on lui dit qu'il doit utiliser le formateur
    # créé précédement et on ajoute ce handler au logger
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # création d'un second handler qui va rediriger chaque écriture de log
    # sur la console
    steam_handler = logging.StreamHandler()
    steam_handler.setLevel(logging.DEBUG)
    logger.addHandler(steam_handler)

    while True:
        try:
            logger.info("Wake up, start working ...")
            request, session = connection(logger)

            timeTupple = remainingTime(request, session, logger)
            if timeTupple:
                hours = (timeTupple[0] * 24) + timeTupple[1]
                minutes = (hours * 60) + timeTupple[2]
                seconds = (minutes + 1) * 60
                logger.info("Ticket valid for {} seconds".format(seconds))
                if seconds > Config.MAX_SLEEP_TIME:
                    seconds = Config.MAX_SLEEP_TIME
                logger.info("Sleep for {} seconds".format(seconds))
                time.sleep(seconds)
            else:# no ticket
                if todayCalendar(request, session, logger, Config.DATABASE):
                    newParking(1, request, session, logger)
                else:
                    time.sleep(Config.SLEEPING_TIME)
        except Exception as e:
            logger.exception("parking.py ended because of unknown exception :(")
