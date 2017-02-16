import functools

from OSBFunctions import openJson, get_id, notTraded, compareItemsCreateList


def highAlchBest(pricesSummaryLoc = "ItemSummary1_23.json", maxLen = 10,
                 priceKeys = ["overall_average", "buy_average", "sell_average"]):
    #open files
    pricesObj = openJson(pricesSummaryLoc)

    #arrays for top 10
    top10Dict ={}
    for key in priceKeys:
        top10Dict[key] = {}
    for key in top10Dict:
        top10Dict[key]["List"] = []
    natureRunePrice = (pricesObj[get_id("Nature rune", pricesObj)]["overall_average"])

    #make our compare function
    def compareHighAlch(priceKey,rsItem):
        storePrice = pricesObj[rsItem]["sp"]
        highAlch = .6 * int(storePrice)
        exchangePrice = pricesObj[rsItem][priceKey]
        if exchangePrice == 0:
            raise notTraded
        cost = exchangePrice + natureRunePrice
        profit = highAlch - cost
        return profit

    #loop to populate our lists
    for key in top10Dict:
        curList = top10Dict[key]["List"]
        compareFunc = functools.partial(compareHighAlch, key)
        compareItemsCreateList(curList,pricesObj,compareFunc,maxLen)

    #print out the results
    print("Printing out the result of High Alch analysis")
    for key in top10Dict:
        print("Top 10 items ranked give",key,"assumption")
        curList = top10Dict[key]["List"]
        for rsItem in curList:
            print(str(key)+ " " + str(pricesObj[rsItem[0]]["name"]) + " rsItem profit " + str(rsItem[1]))


def findMatchMaking(pricesSummaryLoc = "ItemSummary1_23.json", maxlen = 10):
    # TODO: get some measure of liquidity in here
    '''
    :param pricesSummaryLoc: snapshot (currenlty, should have some history for sanity checks)
    :param maxlen: how many items you want to consider
    :return: nothing, currently just prints to terminal
    '''
    pricesObj = openJson(pricesSummaryLoc)
    curList = []

    def compareMatchMaking(rsItem):
        rsItemObj = pricesObj[rsItem]
        averagePrice = rsItemObj["overall_average"]
        buyingPrice = rsItemObj["buy_average"]
        sellingPrice = rsItemObj["sell_average"]
        if min(averagePrice,buyingPrice,sellingPrice) <= 0:
            raise notTraded
        #TODO remove this and replace with better logic for checking if it's actually traded as well as price prediction
        # if averagePrice>(sellingPrice*1.2):
        #     raise notTraded
        metric = ((sellingPrice*.95 -1) - (buyingPrice*1.05 + 1))/averagePrice
        return metric


    compareItemsCreateList(curList, pricesObj, compareMatchMaking, maxlen)

    for rsItem in curList:
        print("Potential Profit for item", pricesObj[rsItem[0]]["name"], "Is", round(rsItem[1],5), "buy price",
              pricesObj[rsItem[0]]["buy_average"], "sell price", pricesObj[rsItem[0]]["sell_average"],
              "average", pricesObj[rsItem[0]]["overall_average"])


