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
import csv
import pickle
# 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',


HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',
    'cookie': 'redacted cloudflare cookie'
}

RSBUDDY_EXCHANGE_NAMES_URL = 'https://rsbuddy.com/static/exchange/names.json'
RSBUDDY_EXCHANGE_ITEM_ID_PRICE_URL = 'https://api.rsbuddy.com/grandExchange'
GE_EXCHANGE_URL = 'http://services.runescape.com/m=itemdb_oldschool/api/graph/'
GE_HISTORIC_JSON_PRICE_FILE = 'historicPrice.json'
GE_HISTORIC_CSV_PRICE_FILE = 'historic.csv'
OSB_HISTORIC_JSON_PRICE_FILE = 'OSBhistoricPrice.json'
OSB_HISTORIC_CSV_PRICE_FILE = 'osbHistroic.csv'



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

def getPrice(itemID, type='graph', startTime=0, frequency=1440):
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
            count += 3 #once we get to retrying, try 3 as often as your total failures
        time.sleep(timeSleep)
    while len(rerun)>0:
        currentItem = rerun.pop(0)
        print("Retrying " + str(currentItem))
        dictObj[currentItem] = functionObj(currentItem)
        if dictObj[currentItem] == "Delete":
            rerun.append(currentItem)
        time.sleep(timeSleep)
        count -= 1
        if count ==0:
            break




def populateHistoricalJSON(startTime=0, frequency=1440, timeSleep = 4, tries = 3, source = "GE"):
    items= openJson('items.txt')
    historicals = {}
    if source =="GE":
        pricerequestor = functools.partial(getPriceGE)
    else:
        pricerequestor = functools.partial(getPrice, startTime=startTime, frequency=frequency)
    fillJSONfromFunction(historicals, pricerequestor, timeSleep)
    if source=="GE":
        historic_file = open(GE_HISTORIC_JSON_PRICE_FILE,'w')
        f = open('pickledumpGE', 'wb')
        pickle.dump(historicals, f)
        f.close()
    else:
        historic_file = open(OSB_HISTORIC_JSON_PRICE_FILE, 'w')
        f = open('pickledumpOSB', 'wb')
        pickle.dump(historicals, f)
        f.close()
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


def createCSVfromJSON(JSONfile, csvFile, encoding, parserData, parserTS):
    '''First row will have the encoding format for how data will be stored
    in each cell in the first column (decided by the encoding parameter
    , and all the timestamps in the rest of the columns. The parsing parameter
    will be a function that assists with decoding the JSON. Columns should go from oldest to newest
    Ultimately this should let me work with Pandas and do things in terms of arrays
    parserData and parserTS should both take in a JSON obj and an item id
    '''
    items = openJson('items.txt')
    #make hook to remove any ']' or '[' from JSON for OSB
    with open(JSONfile, 'r') as f:
        filestr = f.read()
        print(filestr)
        #jsonstr = filestr.translate(None, "[]""[]")
        #print(jsonstr)
        JSONObj = json.loads(filestr)
    firstLine = True
    csvObj = open(csvFile, 'w', newline='')
    csvwriter = csv.writer(csvObj)
    for i in items:
        dataLine = parserData(i, JSONObj) #This should either be a list with the same number of elements as tsLine or a dict
        if firstLine:
            tsLine = parserTS(i, JSONObj)  # Can control the order of a list when printing to CSV which makes it attractive
            header = tsLine
            header.insert(0, encoding)
            csvwriter.writerow(header)
            firstLine = False
        currentLine = dataLine[:]
        currentLine.insert(0, i) #also insert the item number in the 0th column
        print("testing" + str(currentLine))
        csvwriter.writerow(currentLine)
    csvObj.close()


def updateCSVfromJSON():
    pass


def makeHistoricCSVfromGE(jsonFile = GE_HISTORIC_JSON_PRICE_FILE, csvFile = GE_HISTORIC_CSV_PRICE_FILE, pullData = None):
    #TODO consider putting all of these functions into classes and methods
    encoding = "Daily average price; six month trend"
    def GEJSONparserData(i, JSONObj):
        dailyitemObj = JSONObj[i]["daily"]
        runAvgItemObj = JSONObj[i]["average"]
        timeStamps = dailyitemObj.keys()
        rtimeStamps = sorted(timeStamps)
        prices = []
        for ts in rtimeStamps:
            prices.append(str(dailyitemObj[ts]) + ";" + str(runAvgItemObj[ts]))
        return prices

    def GEJSONparserTS(i, JSONObj):
        itemObj = JSONObj[i]["daily"]
        timeStamps = itemObj.keys()
        rtimeStamps = sorted(timeStamps)
        return rtimeStamps
    if pullData == "full":
        populateHistoricalJSON(source = "GE")
    parserData = functools.partial(GEJSONparserData) #TODO Do I actually need these or could I just pass the function directly?
    parserTS = functools.partial(GEJSONparserTS)
    createCSVfromJSON(jsonFile, csvFile, encoding, parserData, parserTS)

def makeHistoricCSVfromOSB(jsonFile = OSB_HISTORIC_JSON_PRICE_FILE, csvFile = OSB_HISTORIC_CSV_PRICE_FILE, pullData = None):
    encoding = "buyingPrice; buyingCompleted; sellingPrice; sellingCompleted; overallPrice; overallCompleted;"
    def OSBJSONparserData(i, JSONObj):
        row = []
        for line in JSONObj[i]:
            cell = ""
            for stat in encoding.strip().split(";"):
                cell += str(line[stat]) + ";"
            row.append(cell)
        return row
    def OSBJSONparserTS(i, JSONObj):
        ts = []
        for line in JSONObj[i]:
            ts.append(line['ts'])
        return ts
    if pullData == "full":
        populateHistoricalJSON(source = "OSB")
    createCSVfromJSON(jsonFile, csvFile, encoding, OSBJSONparserData, OSBJSONparserTS)









#makeHistoricCSVfromGE()
# populateHistoricalJSON(timeSleep=1, tries=3, source = "OSB")


# print(getPrice(5321,'guidePrice'))

makeHistoricCSVfromOSB('OSBHistoricPrice2.json')


