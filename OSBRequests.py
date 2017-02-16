'''
This will be a library to create different json objects
Need one to for creating a snapshot of prices

Need at least one for creating objects that have a time history

'''
#TODO: Will create text files, OSBFunctions should be able to take text files and object them and  pickle them
#TODO put all text file names in globals at the top
import json
import requests
from selenium import webdriver
import time
import pickle
from OSBFunctions import openJson
# 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',


HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',
    'cookie': 'redacted cloudflare cookie'
}

RSBUDDY_EXCHANGE_NAMES_URL = 'https://rsbuddy.com/static/exchange/names.json'
RSBUDDY_EXCHANGE_ITEM_ID_PRICE_URL = 'https://api.rsbuddy.com/grandExchange'


# def get_price(item_id):
#     price = json.loads(requests.get(RSBUDDY_EXCHANGE_ITEM_ID_PRICE_URL + str(item_id), headers=HEADERS).text)
#     print(price)
#     return price['overall']

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



def getPrice(itemID, type='graph', startTime=time.time()*1000, frequency=1440):
    '''
    :param itemID: ID to pass in
    :param type: 'graph' to get timestamped based prices
    , 'guidePrice' to get current buy/sell and quantities
    :param startTime: miliseconds since 1/1 1970
    :param frequency: how
    :return:js Obbject with properties depdendent on the type  parameter.
    'guidePrice' returns:
    {"overall":206,"buying":207,"buyingQuantity":598437,"selling":206,"sellingQuantity":564859}
    'graph' returns:{"ts":ttt,"buyingPrice":209,"buyingCompleted":589394,"sellingPrice":208,
        "sellingCompleted":404612,"overallPrice":208,"overallCompleted":994006}]
    '''
    startTime=int(startTime)
    url = RSBUDDY_EXCHANGE_ITEM_ID_PRICE_URL + '?a=' +str(type)     + '&start=' +str(startTime) + \
          '&g=' + str(frequency) +'&i=' +str(itemID)
    print(url)
    price = json.loads(requests.get(url,headers=HEADERS).text)

    return price


def populateHistorical(startTime=time.time(), frequency=8000,timeSleep =.5):
    items= openJson('items.txt')
    historicals = {}
    for i in items:
        historicals[i]=getPrice(i,'graph',startTime,frequency)
        time.sleep(timeSleep)
        if len(historicals)>10:
            break
    historic_file = open('historicPrice','w')
    historic_file.write(str(historicals))
    historic_file.close()

def populateCurrentOpenOrders(timeSleep=.5):
    items = openJson('items.txt')
    currentOpen = {}
    for i in items:
        currentOpen[i] = getPrice(i,'guidePrice')
        time.sleep(timeSleep)
        if len(currentOpen)>10:
            break
    currentOpen_file = open('currentOpen','w')
    currentOpen_file.write(json.dumps(currentOpen))
    currentOpen_file.close()

populateCurrentOpenOrders()






populateHistorical()




