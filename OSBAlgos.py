import functools

from OSBFunctions import open_json, get_id, NotTraded, compare_items_create_list, rsItem, pricesDict


def highAlchBest(pricesSummaryLoc = "ItemSummary1_23.json", maxLen = 10,
                 priceKeys = ["overall_average", "buy_average", "sell_average"]):
    #open files
    pricesObj = open_json(pricesSummaryLoc)

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
        compare_items_create_list(curList, pricesObj, compareFunc, maxLen)

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
    pricesObj = open_json(pricesSummaryLoc)
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


    compare_items_create_list(curList, pricesObj, compareMatchMaking, maxlen)

    for rsItem in curList:
        print("Potential Profit for item", pricesObj[rsItem[0]]["name"], "Is", round(rsItem[1],5), "buy price",
              pricesObj[rsItem[0]]["buy_average"], "sell price", pricesObj[rsItem[0]]["sell_average"],
              "average", pricesObj[rsItem[0]]["overall_average"])



def betterMatchMaking( price_file = 'currentOpen', maxlen = 10, minProfit = 200000, maxSpending = 40000000, volLimit=10):
    pricesObj = pricesDict()
    pricesObj.addOpen()
    curList = []

    def compareMatchMaking(minProfit, maxSpending, rsItem):
        try:
            buyingPrice = rsItem['buying']
            sellingPrice = rsItem['selling']
            volume = min(rsItem['buyingQuantity'], rsItem['sellingQuantity'])
        except KeyError:
            return 0
        profitPer = (sellingPrice-1) - (buyingPrice+1)

        if profitPer<0:
            return 0
        if volume<volLimit:
            return 0
        if volume * profitPer < minProfit:
            return 0
        if (minProfit/(profitPer))*sellingPrice>maxSpending:
            return 0
        else:
            metric = profitPer/buyingPrice
            rsItem['profit'] = profitPer
            return metric

    compareFunc = functools.partial(compareMatchMaking,minProfit,maxSpending)

    compare_items_create_list(curList, pricesObj, compareFunc, maxlen)

    for group in curList:
        rsItem = group[0]
        print("Potential profit for ", rsItem.name, " is ", rsItem['profit'],
              " Buy Price ", rsItem['buying'], "Sell Price ", rsItem['selling'], "buy Quantity ",
              rsItem['buyingQuantity'], " Sell Quantity ", rsItem['sellingQuantity']," ID is ", rsItem.ID)

betterMatchMaking()