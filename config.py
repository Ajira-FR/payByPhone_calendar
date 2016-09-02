# coding: utf-8

class Config:
    #use by bottleCalendar.py
    DATABASE    = "parking.db"
    LOGIN       = "user"
    PASSWORD    = "user.user"
    HOST        = "192.168.1.13"
    PORT        = "60"
    DEBUG       = True
    SERVER      = "paste"

    #use by parking.py
    MAX_SLEEP_TIME  = 2 * 60 * 60  # 2 hours
    SLEEPING_TIME   = 15 * 60  # 15 min
    URL             = "https://m.paybyphone.fr/default.aspx"
    PHONE_NUMBER    = "06********" #insert phone number there
    PIN             = "****" # paybyphone password
    PARKING_CODE    = "***" #change with your resident code
    CAR_ID          = "*****" #change with your vehicule id
    LOGGER          = "parking.log"

