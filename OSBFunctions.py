import json
import operator


#TODO add a way to apply multiple metrics to compile a list
#TODO find a way to compute different metrics (especially those that require server requests


class notTraded(Exception):
    pass


def get_id(name, names):
    for k, v in names.items():
        if v["name"]==name:
            return k

def openJson(fileLoc):
    file = open(fileLoc,"r")
    Obj = ""
    for line in file:
        Obj += line
    Obj = json.JSONDecoder().decode(Obj) #TODO figure out why I can't use json.loads instead of JSONDecoder/all this
    return Obj

def compareItemsCreateList (curList, pricesObj, comparisonKey, maxLen):
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
        except notTraded:
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

class pricesDict(object):
    def __init__(self):
        self.items = []
        items = openJson('items.txt')
        for i in items:
            self.items.append(rsItem(i,items[i]['name']))
    def addOpen(self):
        '''

        :return: Populates rsItems with "BuyingQuantity", "Buying" (price), "Selling" (price), "Selling Quantity", and
        "Overall" (Price)
        '''
        currentOpen = openJson('currentOpen')
        for item in self.items:
            if item.ID in currentOpen:
                for key in currentOpen[str(item.ID)]:
                    item[key] = currentOpen[item.ID][key]


#


