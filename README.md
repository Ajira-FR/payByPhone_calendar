# payByPhone_calendar
An HTML calendar with a Python back-end to manage PayByPhone parking ticket.
You need to have a paybyphone.com account and a vehicule to use this application.

![calendar](http://img11.hostingpics.net/pics/257876calendar.png)

##Dependencies

* bottle
* bottle_sqlite
* bs4 (beautifulSoup3)
* sqlite3
* requests


##First launch
1. Edit the `parking.py` file with :
```python
ARG1 = {
    'ctl00$ContentPlaceHolder1$CallingCodeDropDownList': '-3',
     'ctl00$ContentPlaceHolder1$AccountTextBox': '06********', #insert phone number there
     'ctl00$ContentPlaceHolder1$PinOrLast4DigitCcTextBox': '****', #password
     'ctl00$ContentPlaceHolder1$RememberPinCheckBox': 'on',
     'ctl00$ContentPlaceHolder1$LoginButton': 'se connecter'
}

ARG2 = {
    '__EVENTTARGET': '',
    '__EVENTARGUMENT': '',
    'ctl00$ContentPlaceHolder1$PreviousLocationDropDownList': '****', #change with your resident code
    'ctl00$ContentPlaceHolder1$LocationNumberTextBox': '',
    'ctl00$ContentPlaceHolder1$NextButton': 'suivant'
}

ARG3 = {
    '__EVENTTARGET': '',
    '__EVENTARGUMENT': '',
    'ctl00$ContentPlaceHolder1$SelectVehicleDropDownList': '*****', #change with your vehicule id
    'ctl00$ContentPlaceHolder1$DurationTextBox': '1',
    'ctl00$ContentPlaceHolder1$TimeUnitDropDownList': '3',
    'ctl00$ContentPlaceHolder1$NextButton': 'suivant'
}
```
2. Change login/password in `bottleCalendar.py` in the authentification function (yes it's ugly, i have to change it) :
```python
def authentification(login, password):
    return login == 'user' and password == "user"
```

3. If you want to access to your calendar over Internet put your IP at the end of `bottleCalendar.py`:
```python
run(host='localhost', port=8088, debug=True)
```
**Warning** : Bottle use basic authentification that is absolutly not secure (login/password with base64 encoding) please be careful and use a secure transport layer like SSL/TLS or VPN !

##How to use it
1. Start frontend :
```bash
python bootleCalendar.py
```
2. Start backend :
```bash
python parking.py
```
I recommand using `screen` linux command on each file

##How it's work
1. Click on the day you want to have a parking ticket -> it become yellow.
2. The date is stored in the sqlite database `parking.db`
3. Every 15 minutes (you can change it) `parking.py` will check if a ticket is needed. if so, it will buy a one day (you can change it) ticket and go to sleep.

##TODO
* Add the possibility to buy an half day ticket, maybe choose wich hour you want,
* Change the paybyphone unofficial API I made with something proper,
* Add a secure login,
* Add the possibility to force refresh to not have to wait that the parking.py daemon wake up,
* Add the possibility to stop a current parking ticket.
