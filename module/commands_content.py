from genericpath import exists
from http.client import ResponseNotReady
import json, requests
from posixpath import split
from pickle import TRUE
import random as rand
import utilities as util
from datetime import datetime
from binance.spot import Spot

FIXERIOFXAPI_URL = "http://data.fixer.io/api/latest?access_key=419f3befde9b7e362bc748d9c767a966&symbols=USD,PHP,JPY,RUB,KRW&format=1"
P2PAPI_URL = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"

# CoinGeckoAPI coins list
coins = {}
while coins == {}:
    coins = requests.get("https://api.coingecko.com/api/v3/coins/list").json()

with open("json\\bepisLB.json", "r") as bepisLB_file:
    bepisLB = json.load(bepisLB_file)
    bepisLB_file.close()

with open("json\\seggsLB.json", "r") as seggsLB_file:
    seggsLB = json.load(seggsLB_file)
    seggsLB_file.close()

with open("json\\gagofy.json", "r") as gagofy_file:
    gagofyData = json.load(gagofy_file)
    gagofy_file.close()

with open("json\\mooncycle.json", "r") as moon_file:
    moonData = json.load(moon_file)
    moon_file.close()


def spot(pair, k, s, user):
    util.logger(str(user) + " used spot for " + pair)
    bin_client = Spot(key=k, secret=s)
    s = "```From Binance Spot:\n\n"
    if str.lower(pair) == "all":
        watchlist = [
            "BTCUSDT",
            "ETHUSDT",
            "LRCUSDT",
            "ADAUSDT"
        ]
        
        for x in range(0, len(watchlist)):
            res = bin_client.ticker_price(watchlist[x])
            s += "" + watchlist[x] + ":\t" + res["price"] + "\n"
    else:
        res = bin_client.ticker_price(pair)
        s += "" + pair + ":\t" + res["price"] + "\n"

    return s + "```"


def fx(user):
    util.logger(str(user) + " used fx")
    response = requests.get(FIXERIOFXAPI_URL) 
    s = ("```"
    "from: data.fixer.io/api\n\n"
    "PHP/USD:\t" + str(float(response.json()["rates"]["PHP"])/float(response.json()["rates"]["USD"])) + "\n"
    "PHP/EUR:\t" + str(response.json()["rates"]["PHP"]) + "\n"
    "PHP/JPY:\t" + str(float(response.json()["rates"]["PHP"])/float(response.json()["rates"]["JPY"])) + "\n"
    "PHP/RUB:\t" + str(float(response.json()["rates"]["PHP"])/float(response.json()["rates"]["RUB"])) + "\n"
    "PHP/KRW:\t" + str(float(response.json()["rates"]["PHP"])/float(response.json()["rates"]["KRW"])) + "\n"
    "```")
    return s

# allows user to get notified when Binance P2P PHP/USDT rate crosses inputted rate
# 5 secs refresh: to be implemented
def p2pnotify(user, msg):
    try:
        list = msg.split(" ")
        rate = float(list[2])
        return "<@" + str(user) + "> will be notified once PHP/USDT P2P buy rate is below or equal to " + str(f'{rate:0.2f}')
    except:
        return "Invalid p2p notify command! Please check rate inputted!"
    
# returns 1 Binance P2P USDT/PHP result with the lowest buying rate
def p2p(tradeType, payMethod, user):
    util.logger(str(user) + " used p2p for " + tradeType)
    data = {
        "asset": "USDT",
        "fiat": "PHP",
        "merchantCheck": True,
        "page": 1,
        "publisherType": "merchant",
        "rows": 5,
        "tradeType": tradeType,
    }

    if payMethod != "":
        data.update({"payTypes": [payMethod]})

    try:
        response = requests.post(P2PAPI_URL, json=data)
        r_data = response.json()
        if len(r_data["data"]) == 0:
            raise Exception
    except:
        s = ("```Invalid p2p options entered!\n\n"
            "p2p (buy|sell) (gcash|ing|bank|ubop)"
            "```"
        )
        return s

    s = "```Binance P2P PHP/USDT " +  tradeType
    if payMethod != "":
        s += " for pay method " + payMethod
    s += "\n\n"

    i = 0
    for x in r_data["data"]:
        payMethods = ""
        for y in r_data["data"][i]["adv"]["tradeMethods"]:
            payMethods += str(y["payType"]) + " "

        s += (
            "Binance P2P PHP/USDT:   " + str(r_data["data"][i]["adv"]["price"]) + "\n"
            "Available USDT:         " + str(r_data["data"][i]["adv"]["surplusAmount"]) + "\n"
            "Merchant Name:          " + str(r_data["data"][i]["advertiser"]["nickName"]) + "\n"
            "Payment methods:        " + payMethods + "\n"
            "================================================\n\n"
        )
        i+=1

    s += "```"

    return s

# return next new moon and full moon dates
# from manual list fetched from "https://www.timeanddate.com/moon/phases/@220244"
def whenmoon(user):
    util.logger(str(user) + " used whenmoon")
    currentDate = datetime.today()
    fullMoonSTR = ""
    newMoonSTR = ""

    for x in moonData["fullmoons"]:
        loopDate = datetime.strptime(x, '%d/%m/%Y')
        if currentDate < loopDate:
            fullMoonSTR = datetime.strftime(loopDate, '%B %d %Y')
            break
    
    for x in moonData["newmoons"]:
        loopDate = datetime.strptime(x, '%d/%m/%Y')
        if currentDate < loopDate:
            newMoonSTR = datetime.strftime(loopDate, '%B %d %Y')
            break

    return "```Next FULL moon:  " + fullMoonSTR + "\nNext NEW moon:   " + newMoonSTR + "```"

# CoinGeckoAPI can only show rates against USD
# had to make a workaround for token-token rates
def crypto(cg, args, user):
    util.logger(str(user) + " queried " + args)
    result = {}
    result2 = {}
    s = "```From CoinGecko:\n\n"
    try:
        list = args.split(" ")
        if len(list) == 1:
            return "```Input a valid token!```"
        else:
            coin1 = list[1]
            coin1_ID = util.getCoinID(coin1.lower(), coins)[0]["id"]
            while result == {}:
                try:
                    result = cg.get_price(ids=coin1_ID, vs_currencies='usd')
                except:
                    pass
            if len(list) > 2:
                coin2 = list[2]
                coin2_ID = util.getCoinID(coin2.lower(), coins)[0]["id"]
                while result2 == {}:
                    try:
                        result2 = cg.get_price(ids=coin2_ID, vs_currencies='usd')
                    except:
                        pass
                s += ""+ coin1_ID + "/" + coin2_ID + "  " + coin1.upper() + "/" + coin2.upper() + " : " + str(result[coin1_ID]['usd']/result2[coin2_ID]['usd'])

            s += "" + coin1_ID + "  " + coin1.upper() + "/USD : " + str(result[coin1_ID]['usd'])
    except:
        return "```Input a valid token!```"
    return s + "```"


# gacha game to monke bepis
def bepisMonke(user):
    result = ""
    record = {}
    num = rand.randint(0,1000)
    appendRecord = False

    try:
        record = list(filter(lambda x:x["user"]==user,bepisLB))[0]
        print(record)
        if record == []:
            raise ValueError
    except:
        print("New player " + user)
        record = {
            "user" : user,
            "tries" : 0,
            "wins" : 0
        }
        appendRecord = True

    record["tries"] += 1
    
    util.logger(user + " rolled " + str(num) + " in bepisMonke")

    if num < 69:
        space = int(num/2) * " "
        result =  "||" + space + "bepis monke" + space + "||"
        record["wins"] += 1
    elif num == 69:
        result = "|| https://imgur.com/e54X8Pu ||" 
        record["wins"] += 1

    if appendRecord:
        bepisLB.append(record)
    with open("bepisLB.json", "w") as bepisLB_file:
        json.dump(bepisLB, bepisLB_file)
        bepisLB_file.close()

    return result

# gacha game for seggs
def seggs(user):
    result = ""
    record = {}
    num = rand.randint(0,1000)
    appendRecord = False

    try:
        record = list(filter(lambda x:x["user"]==user,seggsLB))[0]
        print(record)
        if record == []:
            raise ValueError
    except:
        print("New player " + user)
        record = {
            "user" : user,
            "tries" : 0,
            "wins" : 0
        }
        appendRecord = True

    record["tries"] += 1

    util.logger(str(user) + " rolled " + str(num) + " in seggs")

    if num < 43:
        record["wins"] += 1
        result = "https://imgur.com/cZNc7Pl"

    if appendRecord:
        seggsLB.append(record)
    with open("seggsLB.json", "w") as seggsLB_file:
        json.dump(seggsLB, seggsLB_file)
        seggsLB_file.close()

    return result


def winrate(user):
    util.logger(str(user) + " queried winrate")
    recordB = {}
    recordS = {}
    returnMsg = "```Winrates for " + user + "\n"
    #try:
    #    recordB = list(filter(lambda x:x["user"]==user,bepisLB))[0]
    #    if recordB == []:
    #        raise ValueError
    #    winRateB = recordB["wins"]/recordB["tries"]* 100
    #    winRateB_str = "{:.2f}".format(winRateB)
    #    returnMsg = returnMsg + "bepis:   " + str(recordB["tries"]) + "/" + str(recordB["wins"]) + "(" + str(winRateB_str) + "%)\n"
    #except:
    #    returnMsg = returnMsg + "Haven't played bepis gacha\n"
    try:
        recordS = list(filter(lambda x:x["user"]==user,seggsLB))[0]
        if recordS == []:
            raise ValueError
        winRateS = recordS["wins"]/recordS["tries"]* 100
        winRateS_str = "{:.2f}".format(winRateS)
        returnMsg = returnMsg + "seggs:   " + str(recordS["tries"]) + "/" + str(recordS["wins"]) + "(" + str(winRateS_str) + "%)\n"
    except:
        returnMsg = returnMsg + "Haven't played seggs gacha\n"

    return returnMsg + "```"


def leaderboard(user, msg):
    record = []

    try:
        list = msg.split(" ")
        game = list[1]
        if game not in ("seggs", "seggs"):
            raise ValueError
    except:
        util.logger(str(user) + " asked for LB of an invalid game: " + msg)
        return "```Game not found!```"
    util.logger(str(user) + " asked for LB of " + game)


    returnMsg = "```LEADERBOARD FOR "+ game +"\n\nUser\t\t\t\t\t\t\t\t\t|  Winrate  |  Tries  |  Wins  |\n"
    try:
        #if game == "bepis":
        #    record = sorted(bepisLB, key=lambda item: item["wins"]/item["tries"]*100, reverse=True)
        if game == "seggs":
            record = sorted(seggsLB, key=lambda item: item["wins"]/item["tries"]*100, reverse=True)
            if record == []:
                raise ValueError
    except:
        return "```No leaderboard for " + game + " game```"

    ctr = 0
    for x in record:
        winrate = "{:05.2f}".format(x["wins"]/x["tries"]*100)
        winrateStr = winrate + int(7 - len(winrate)) * " "
        tries = str(x["tries"]) + int(7 - len(str(x["tries"]))) * " "
        wins = str(x["wins"]) + int(6 - len(str(x["wins"]))) * " "
        returnMsg = returnMsg + x["user"] + str(int(40 - len(x["user"])) * " ") + "|  " + winrateStr + "  |  " + tries + "|  " + wins + "|\n"
        ctr+=1
        if ctr == 5: break


    returnMsg = returnMsg + "```"
    return returnMsg

def help(user):
    util.logger(str(user) + " queried help")
    s = ("```AVAILABLE COMMANDS:\n"
            "only in #bot-spam and #crypto:\n"
            "^spot [binance pairing ex: BTCUSDT]\n"
            "^fx\n"
            "^p2p [buy|sell [gcash|ubop|bank|ing|others...]]\n"
            "^price <coin1> <coin2(optional)>\n\n"
            "only in #degeneral:\n"
            "^gagofy"
            "\n\n"
            "required = ()\n"
            "optional = []\n"
            "```"
        )
    return s

def loadConfig():
    return util.loadJsonFile("json\\config.json", "r")

def gagofy(user):
    util.logger(str(user) + " queried gagofy")
    length = len(gagofyData["statements"])
    randNum = rand.randint(0, length - 1)
    return gagofyData["statements"][randNum]