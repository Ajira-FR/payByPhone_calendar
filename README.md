# payByPhone_calendar
An HTML calendar with a Python back-end to manage PayByPhone parking ticket.
You need to have a paybyphone.com account and a vehicule to use this application.

![calendar](http://img11.hostingpics.net/pics/257876calendar.png)

#Dependencies

* bottle
* bottle_sqlite
* bs4 (beautifulSoup3)
* sqlite3
* requests

#How to installation
1. (optional) Create a virtual environnement :
```bash
virtualenv myvenv
source myvenv/bin/activate
```
2. Install requierment : `python setup.py install`

#First launch
1. Edit the `config.py` file as you want :
```python
class Config:
    #use by bottleCalendar.py
    DATABASE    = "parking.db"
    LOGIN       = "user"
    PASSWORD    = "user.user"
    HOST        = "localhost"
    PORT        = "8088"
    DEBUG       = True

    #use by parking.py
    MAX_SLEEP_TIME  = 2 * 60 * 60  # 2 hours
    SLEEPING_TIME   = 15 * 60  # 15 min
    URL             = "https://m.paybyphone.fr/default.aspx"
    PHONE_NUMBER    = "06********" #insert phone number there
    PIN             = "****" # paybyphone password
    PARKING_CODE    = "***" #change with your resident code
    CAR_ID          = "*****" #change with your vehicule id
    LOGGER          = "parking.log"
```
2. Don't forget to change `LOGIN` and `PASSWORD`
3. If you want to access to your calendar over Internet put your IP in `HOST` and port in `PORT`

**Warning** : Bottle use basic authentification that is absolutly not secure (login/password with base64 encoding) please be careful and use a secure transport layer like SSL/TLS or VPN !

#How to use it
1. Start frontend :
```bash
python bootleCalendar.py
```
2. Start backend :
```bash
python parking.py
```
I recommand using `screen` linux command on each file

#How it's work
1. Click on the day you want to have a parking ticket -> it become yellow.
2. The date is stored in the sqlite database `parking.db`
3. Every 15 minutes (you can change it) `parking.py` will check if a ticket is needed. if so, it will buy a one day (you can change it) ticket and go to sleep.

#TODO
* Add the possibility to buy an half day ticket, maybe choose wich hour you want,
* Change the paybyphone unofficial API I made with something proper,
* Add a secure login,
* Add the possibility to force refresh to not have to wait that the parking.py daemon wake up,
* Add the possibility to stop a current parking ticket.
