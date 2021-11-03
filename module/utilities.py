from datetime import datetime
import os
import json

if not os.path.exists('logs'):
    os.makedirs('logs')

# general functions
def loadJsonFile(filename, mode):
    if os.path.exists(filename):
        f = open(filename, mode, encoding="utf8")
        return json.load(f)
    return FileExistsError

def logger(message):
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y")
    ts_string = now.strftime("%d/%m/%Y %H:%M:%S")

    if os.path.exists("logs/log_" + dt_string + ".log"):
        f = open("logs/log_" + dt_string + ".log", "a")
    else:
        f = open("logs/log_" + dt_string + ".log", "x")
    f.write(ts_string + "  ---  " + message + "\n")
    f.close()


# crypto() functions
def getCoinID(arg, coins):
    return list(filter(lambda x:x["Symbol"]==arg,coins))