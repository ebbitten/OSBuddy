'''
This will be a library to create different json objects
Need one to for creating a snapshot of prices

Need at least one for creating objects that have a time history

'''
#TODO: Will create text files, OSBFunctions should be able to take text files and object them and  pickle them
#TODO put all text file names in globals at the top
#TODO figure out a way to be able to pause and resume the long queries
import json
import requests
from selenium import webdriver
import time
import datetime
import pickle
from OSBFunctions import openJson
import functools
# 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',


HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',
    'cookie': 'redacted cloudflare cookie'
}

RSBUDDY_EXCHANGE_NAMES_URL = 'https://rsbuddy.com/static/exchange/names.json'
RSBUDDY_EXCHANGE_ITEM_ID_PRICE_URL = 'https://api.rsbuddy.com/grandExchange'
GE_EXCHANGE_URL = 'http://services.runescape.com/m=itemdb_oldschool/api/graph/'




def get_id(name, names):
    for k, v in names.items():
        if v["name"]==name:
            return k

def getOSBuddySummary():
    '''

    :return: Javascript Object of the following form but for all items:
    {"2": {"sp": 5, "name": "Cannonball", "buy_average": 205, "id": 2,
    "overall_average": 207, "sell_average": 206, "members": true}}
    '''
    names = getElementByBrowser(RSBUDDY_EXCHANGE_NAMES_URL)
    items_file = open('item.txt', 'w')
    items_file.write(names)
    items_file.close()
    base_prices = getElementByBrowser(RSBUDDY_EXCHANGE_ITEM_ID_PRICE_URL)
    prices_file = open('prices.txt', 'w')
    prices_file.write(base_prices)
    prices_file.close()

def getElementByBrowser(url=RSBUDDY_EXCHANGE_NAMES_URL, element='/html/body'):
    browserObj = webdriver.WebDriver()
    browserObj.get(url)
    time.sleep(5)
    print(browserObj)
    elem = browserObj.find_element_by_xpath(element)
    return elem.text

def queryPrice(url):
    '''
    takes in a url, returns a JSON object
    :param url:
    :return:
    '''
    print(url)
    try:
        price = json.loads(requests.get(url,headers=HEADERS).text)
        return price
    except :
        #TODO update this so that it can be used to return an error log that can be autoreplayed
        print("Failed with ")
        print(url)
        return "Delete"

def getPrice(itemID, type='graph', startTime=time.time()*1000, frequency=1440):
    '''
    :param itemID: ID to pass in
    :param type: 'graph' to get timestamped based prices
    , 'guidePrice' to get current buy/sell and quantities
    :param startTime: miliseconds since 1/1 1970. time.time() returns current milliseconds
    :param frequency: how many minutes
    :return:js Obbject with properties depdendent on the type  parameter.
    'guidePrice' returns:
    {"overall":206,"buying":207,"buyingQuantity":598437,"selling":206,"sellingQuantity":564859}
    'graph' returns:{"ts":ttt,"buyingPrice":209,"buyingCompleted":589394,"sellingPrice":208,
        "sellingCompleted":404612,"overallPrice":208,"overallCompleted":994006}]
    '''
    startTime=int(startTime)
    url = RSBUDDY_EXCHANGE_ITEM_ID_PRICE_URL + '?a=' +str(type)     + '&start=' +str(startTime) + \
          '&g=' + str(frequency) +'&i=' +str(itemID)
    return queryPrice(url)


def getPriceGE(itemID):
    '''
    Gets the price from the OSRS GE, benefit is that it can go back six months
    :param itemID: ID to pass in
    :return: JSON object of the form "ts":price
    '''
    url = GE_EXCHANGE_URL + str(itemID) + ".json"
    return queryPrice(url)

def ts2date(ts):
    dateObj = datetime.date.fromtimestamp(ts/1000)
    print(dateObj.ctime())

def fillJSONfromFunction(dictObj, functionObj, timeSleep = .5, tries = 3):
    '''
    Takes in a dictionary object to populate data from a given source using the function object
    :param dictObj: dictionary that gets filled with information based on the requestor function passed in
    :param functionObj: requestor function to query websites for prices
    :param timeSleep: how long to sleep between requests
    :param tries: how many times to try to get the same item populated, necessary to prevent infinite loop
    :return: Nothing, mutates the dictObj though
    '''
    items = openJson('items.txt')
    rerun = []
    previousItem = ""
    count = 0
    for i in items:
        dictObj[i] = functionObj(i)
        if dictObj[i] == "Delete":
            rerun.append(i)
        time.sleep(timeSleep)
    while len(rerun>0):
        currentItem = rerun.pop(0)
        if currentItem == previousItem:
            count += 1
            if count == tries:
                break
        else:
            count = 0
        dictObj[currentItem] = functionObj(currentItem)
        if dictObj[currentItem] == "Delete":
            rerun.append(currentItem)
        previousItem = currentItem
        time.sleep(timeSleep)




def populateHistorical(startTime=time.time(), frequency=8000, timeSleep = 4, tries = 3, source = "GE"):
    items= openJson('items.txt')
    historicals = {}
    GEpricerequestor = functools.partial(getPriceGE)
    fillJSONfromFunction(historicals, GEpricerequestor, timeSleep)

    historic_file = open('historicPrice','w')
    historic_file.write(str(historicals))
    historic_file.close()


def populateCurrentOpenOrders(timeSleep=.5):
    items = openJson('items.txt')
    currentOpen = {}
    OSBcurrentRequestor = functools.partial(getPrice,type = 'guideprice' )
    fillJSONfromFunction(currentOpen, OSBcurrentRequestor, timeSleep)
    currentOpen_file = open('currentOpen','w')
    currentOpen_file.write(json.dumps(currentOpen))
    currentOpen_file.close()
    print("Completed populating current orders!")


populateHistorical()

# print(getPrice(5321,'guidePrice'))



