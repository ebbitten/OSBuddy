import json
import operator
import io

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



def highAlchBest(itemsNamesLoc="ItemNames", pricesSummaryLoc = "ItemSummary1_23.json"):
    #open files
    pricesObj = openJson(pricesSummaryLoc)
    natureRune = (pricesObj[get_id("Nature rune",pricesObj)]["overall_average"])
    #arrays for top 10
    top10Dict ={}
    top10Dict["Avg"] = {}
    top10Dict["Best"] = {}
    top10Dict["Worst"] = {}
    for key in top10Dict:
        top10Dict[key]["List"] = []
    #loop to populate
    for rsItem in pricesObj:
        # print(rsItem)
        storePrice = pricesObj[rsItem]["sp"]
        highAlch = .6 * int(storePrice)
        exchangePriceAvg = pricesObj[rsItem]["overall_average"]
        exchangePriceBuy = pricesObj[rsItem]["buy_average"]
        exchangePriceSell = pricesObj[rsItem]["sell_average"]
        if min(exchangePriceSell,exchangePriceBuy,exchangePriceAvg) == 0:
            continue #filter out anything that has any price of 0
        cost = {}
        cost["Avg"] = exchangePriceAvg + natureRune
        cost["Best"] = exchangePriceBuy + natureRune
        cost["Worst"] = exchangePriceSell + natureRune
        for key in top10Dict:
            profit = highAlch - cost[key]
            curList = top10Dict[key]["List"]
            if len(curList) < 10:
                curList.append([pricesObj[rsItem],profit])
            else:
                curMinProfitItem = min(curList, key=operator.itemgetter(1))
                curMinProfit = curMinProfitItem[1]
                if profit > curMinProfit:
                    curList.remove(curMinProfitItem)
                    curList.append([rsItem,profit])
    #print out the results
    for key in top10Dict:
        print("Top 10 items ranked give",key,"assumption")
        curList = top10Dict[key]["List"]
        curList.sort(key = operator.itemgetter(1))
        for rsItem in curList:
            print("rsItem name " + str(pricesObj[rsItem[0]]["name"]) + " rsItem profit " + str(rsItem[1]))







    # prices = json.loads(pricesObj)
    # print("loaded json", prices)
    # for line in prices_file:
    #     print(line)

highAlchBest()

