import json
import operator


class NotTraded(Exception):
    pass


def get_id(name, names):
    for k, v in names.items():
        if v["name"]==name:
            return k


def open_json(fileLoc):
    file = open(fileLoc,"r")
    Obj = ""
    for line in file:
        Obj += line
    Obj = json.JSONDecoder().decode(Obj) #TODO figure out why I can't use json.loads instead of JSONDecoder/all this
    return Obj


def compare_items_create_list (curList, pricesObj, comparisonKey, maxLen):
    '''
    :param curList: list that's manipulated in place
    :param pricesObj: JSON object that has all of the price data for a snapshot
    :param comparisonKey: function that only accepts rsItem as a parameter (may assume priceObj)
    and should be used to compare
    :param maxLen: how long you want the list to be
    :return: Nothing
    '''
    for rsItem in pricesObj.items:
        try:
            metric = comparisonKey(rsItem)
        except NotTraded:
            continue
        if len(curList) < maxLen:
            curList.append([rsItem, metric])
        else:
            curMinMetricItem = min(curList, key=operator.itemgetter(1))
            curMinMetric = curMinMetricItem[1]
            if metric > curMinMetric:
                curList.remove(curMinMetricItem)
                curList.append([rsItem, metric])
    curList.sort(key=operator.itemgetter(1))


class rsItem (dict):
    def __init__(self,ID,name):
        #comes from items.txt
        self.ID = ID
        self.name = name
        #comes from currentOpen.txt
        self.buyingQuantity=0
        self.buying=0
        self.selling=0
        self.sellingQuantity=0
        self.overall = 0
        #Is populated druing runs
        self.profit = 0
        self.metric = 0
#TODO figure out why I can't populate any of the above at run time, also why can it only be called in bracket notation?


class pricesDict(object):
    def __init__(self):
        self.items = []
        items = open_json('data/items.txt')
        for i in items:
            self.items.append(rsItem(i,items[i]['name']))
    def addOpen(self):
        '''

        :return: Populates rsItems with "BuyingQuantity", "Buying" (price), "Selling" (price), "Selling Quantity", and
        "Overall" (Price)
        '''
        currentOpen = open_json('data/currentOpen')
        for item in self.items:
            if item.ID in currentOpen:
                for key in currentOpen[str(item.ID)]:
                    item[key] = currentOpen[item.ID][key]


def createPandasFromCSV(csv, pandasDataFrame):
    pass