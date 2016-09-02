# coding: utf-8
from bottle import route, run, template, request, static_file, install, auth_basic
import calendar
from datetime import datetime
from time import mktime
import json
from bottle_sqlite import SQLitePlugin
import locale
from config import Config

locale.setlocale(locale.LC_TIME, '')
install(SQLitePlugin(dbfile = Config.DATABASE))

def authentification(login, password):
    return login == Config.LOGIN and password == Config.PASSWORD

def jsonButton(href, htmlClass, dataCalendarNav, text):
    return {"href" : href, "class" : htmlClass, "data-calendar-nav" : dataCalendarNav, "text" : text}

def jsonCell(htmlClass, id, text, style=None, onClick=None):
    j = {"td" : {"class" : htmlClass, "id" : id}, "text" : text}
    if style:
        j["td"]["style"] = style
    if onClick:
        j["td"]["onClick"] = onClick
    return j

def createHTMLCalendar(year, month, today, db):
    cal = calendar.Calendar()
    iterDate = cal.itermonthdates(year, month)

    htmlData = {"month" : datetime(year, month, 1).strftime("%B"), "year" : year, "button" : [], "tableBody" : []}
    if month > today.month:
        prevMonth = month - 1
        prevYear = year
        if prevMonth < 1:
            prevMonth = 12
            prevYear -= 1
        htmlData["button"].append(jsonButton("?year={}&month={}".format(prevYear, prevMonth), "btn btn-primary", "prev", "<< Avant"))
    htmlData["button"].append(jsonButton("?year={}&month={}".format(today.year, today.month), "btn btn-default", "today", "Aujourd'hui"))
    if not (year == 3000 and month == 12):
        nextMonth = month + 1
        nextYear = year
        if nextMonth > 12:
            nextYear += 1
            nextMonth = 1
        htmlData["button"].append(jsonButton("?year={}&month={}".format(nextYear, nextMonth), "btn btn-primary", "next", "Après >>"))

    rows = db.execute("SELECT timestamp FROM parking WHERE timestamp >= ?", (mktime(datetime(year, month, 1).timetuple()),)).fetchall()
    registeredDays = []
    if len(rows) > 0 :
        for raw in rows:
            registeredDays.append(raw[0])
    col = 0
    for day in iterDate:
        timestamp = mktime(day.timetuple())
        htmlClass = "cell"
        style = None
        onClick = None

        if today.year == day.year and today.month == day.month and today.day == day.day:
            htmlClass += " today"
        if day.month != month:
            htmlClass += " out"
        elif col == 5 or col == 6:
            htmlClass += " weekend"
        elif mktime(today.timetuple()) > timestamp:
            htmlClass += " closed"
            if timestamp in registeredDays:
                style = "color:yellow"
        else:
            htmlClass += " good"
            onClick = "ProcessDate(this.id)"
            if timestamp in registeredDays:
                style = " background-color:yellow"

        htmlData["tableBody"].append(jsonCell(htmlClass, day, day.day, style=style, onClick=onClick))
        col = (col + 1) % 7
    return template("tableHdr.html", data=htmlData)

@route('/_add_day', apply=[auth_basic(authentification)])
def addDay(db):
    today = datetime.today()
    today = datetime(today.year, today.month, today.day)
    debug = "OK"
    id = request.params.get("data", 0)
    try:
        date = datetime.strptime(id, "%Y-%m-%d")
        if date >= today:
            timestamp = mktime(date.timetuple())
            db.execute("INSERT INTO parking (timestamp, halfDay) VALUES(?, ?)", (timestamp, 0))
            db.commit()
    except ValueError as ve:
        debug = "ERROR"

    return json.dumps({'id':id, 'debug':debug})

@route('/_remove_day', apply=[auth_basic(authentification)])
def removeDay(db):
    id = request.params.get("data", 0)
    debug = "OK"
    try:
        date = datetime.strptime(id, "%Y-%m-%d")
        timestamp = mktime(date.timetuple())
        db.execute("DELETE FROM parking WHERE timestamp = ?", (timestamp,))
        db.commit()
    except ValueError as ve:
        debug = "ERROR"

    return json.dumps({'id':id})

@route("/bottleCalendar.css")
def css():
    return static_file("bottleCalendar.css", root='.')

@route('/', apply=[auth_basic(authentification)])
def index(db):
    today = datetime.today()
    year = today.year
    month = today.month
    getYear = request.query.year
    getMonth = request.query.month
    if getYear and getMonth:
        getYear = int(getYear)
        getMonth = int(getMonth)
        if getYear > 1970 and getYear <= 3000 and getMonth > 0 and getMonth <= 12:
            year = getYear
            month = getMonth
    today = datetime(today.year, today.month, today.day)
    return createHTMLCalendar(year, month, today, db)

run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG, server=Config.SERVER)
