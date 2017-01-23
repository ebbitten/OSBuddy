'''
This will be a library of all the functions I might want while operating stockFighter

'''



import json
import requests

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'cookie': 'redacted cloudflare cookie'
}

RSBUDDY_EXCHANGE_NAMES_URL = 'https://rsbuddy.com/static/exchange/names.json'
RSBUDDY_EXCHANGE_ITEM_ID_PRICE_URL = 'https://api.rsbuddy.com/grandExchange?a=guidePrice&i='


def get_id(name, names):
    for k, v in names.items():
        if v['name'] == name:
            return k


def get_price(item_id):
    price = json.loads(requests.get(RSBUDDY_EXCHANGE_ITEM_ID_PRICE_URL + str(item_id), headers=HEADERS).text)
    return price['overall']


def main():
    names = json.loads(requests.get(RSBUDDY_EXCHANGE_NAMES_URL, headers=HEADERS).text)
    items_file = open('items.txt', 'r')
    prices_file = open('prices.txt', 'w')
    for line in items_file:
        line = line.replace('\n', '')
        prices_file.write(line + ':' + str(get_price(get_id(line, names))) + '\n')
    items_file.close()
    prices_file.close()


main()


global apikey,base_url,header
apikey = '7791d4b66cea4c0fd94b15150300fc378c085074'
base_url = 'https://api.stockfighter.io/ob/api'
#authenticate
header = {'X-Starfighter-Authorization': apikey}
# import libraries
import requests
import json


class starMarket(object):
    def __init__(self,venues,stock,account):
        self.venues=venues
        self.stock=stock
        self.account=account
        self.histAskVol = 0
        self.histAskPrice = 0
        self.histAskNum = 0
        self.histAskAvgVol = 0
        self.histBidVol = 0
        self.histBidPrice = 0
        self.histBidNum = 0
        self.histBidAvgVol = 0
    def orderStock(self, price, qty, direction = 'buy', orderType = 'limit'):
        #Should handle buys/sells of all order types. Default to buy and limit
        # put price, qty, direction, orderType into dictionary
        data={}
        data['price']=price
        data['qty']=qty
        data['direction']=direction
        data['orderType']=orderType
        data['account']=self.account
        #encode data in json so that it gets passed as a string
        data=json.dumps(data)
        #put Venue, stock and 'orders' into the url
        url=base_url+'/venues/'+self.venues+'/stocks/'+self.stock+'/orders'
        r=requests.post(url, data=data, headers=header)
        return(r.json())
        # print(r,r.json()) #currently just in for debugging/confirmation purposes

    # def cancelOrder(self, ): implement get functionality

    # below are all the various "get" methods

    def orderBook(self):
        url = base_url + '/venues/' + self.venues + '/stocks/' + self.stock
        r = requests.get(url)
        # print(r, r.json())
        return r.json()

    def getStockList(self):
        # put venues and 'stocks' into url
        url = base_url + '/venues/' + self.venues + '/stocks'
        r = requests.get(url)
        # print(r, r.json())
        return r.json()


    def heartBeat(self):
        url = base_url + '/venues/' + self.venues + '/heartbeat'
        r = requests.get(url)
        # print(r, r.json())
        return r.json()

    def quoteStock(self):
        url=base_url + '/venues/' + self.venues + '/stocks/' + self.stock + '/quote'
        r = requests.get(url)
        # print(r, r.json())
        return r.json()

    def orderStatus(self,orderID):
        url=base_url + '/venues/' + self.venues + '/stocks/' + self.stock + '/orders/'+str(orderID)
        r = requests.get(url, headers=header)
        # print(r, r.json())
        return r.json()

    def getMyOrders(self):
        url=base_url+'/venues/' + self.venues + '/accounts/' + self.account + '/orders'
        r = requests.get(url, headers=header)
        # print(r, r.json())
        return r.json()

    def getOrdersForStock(self,stock):
        url = base_url + '/venues/' + self.venues + '/accounts/' + self.account + '/stocks/'+ stock + '/orders'
        r = requests.get(url)
        # print(r, r.json())
        return r.json()
    def updatePriceStats(self):
        quote=self.quoteStock()
        if quote['askSize'] > 0:
            self.histAskPrice = ((self.histAskPrice * self.histAskVol) + (quote['ask'] * quote['askSize'])) / (
            self.histAskVol + quote['askSize'])
            self.histAskVol += quote['askSize']
            self.histAskNum +=1
            self.histAskAvgVol =self.histAskVol/self.histAskNum
        if quote['bidSize'] > 0:
            self.histBidPrice = ((self.histBidPrice * self.histBidVol) + (quote['bid'] * quote['bidSize'])) / (
            self.histBidVol + quote['bidSize'])
            self.histBidVol += quote['bidSize']
            self.histBidNum +=1
            self.histBidAvgVol =self.histAskVol/self.histAskNum
    def smartOrder(self,priceStart,margin,direction,volModifier,quote,ordersDict):
        price = int(priceStart * margin)
        if direction=='buy':
            sizeVar='bidSize'
        else:
            sizeVar='askSize'
        quantity = int(min(max(quote[sizeVar] / volModifier, x.histBidAvgVol / volModifier),50))
        orderID = x.orderStock(price, quantity,direction=direction)['id']
        ordersDict[orderID] = [price, quantity]  # Storing in the form "ID: P,Q"



#Test cases for above APIs
# x=starMarket(venues,stock,account)
# x.orderStock(50,50)
# # x.getStocks()
# x.getMyOrders()
# x.getOrdersForStock(stock)
# x.getStockList()
# x.heartBeat()
# x.orderBook()
# stockQuote=x.quoteStock()

#let's start implementing some business logic

import time

def runTrain(amount):
    #Function to beat the breaking apart a share game
    x=starMarket(venues, stock, account)
    qty=50
    quoteTotal=0
    initialQuote=x.quoteStock()
    # print(initialQuote)
    while quoteTotal<(amount):
        for i in range(10): #try re-initializing starMarket
            #Consider adding a line where you cancel/make sure you don't have previous orders
            quote=x.quoteStock()
            try:
                print(quote['ask'], 'current quote')
                ask=quote['ask']
                askSize=quote['askSize']
                print(initialQuote['ask'], ask, 'inital and current quote')
                if initialQuote['ask'] * 1.02 > ask:
                    myBid = int((ask * 1.01))
                    order=x.orderStock(myBid, int(askSize / 100))
                    print(order,order.json())
                    quoteTotal+=int(askSize/100)

                else:
                    time.sleep(.2)
            except KeyError:
                print('error, couldnt find any asks')
                time.sleep(1)
            # bid=quote['bid']
            time.sleep(.1)
        # x=starMarket(venues, stock, account)




def stealTrain(profPercent,buyMargin,sellMargin,volModifier,lowOpp,highOpp,currentStocks=0,adjFactor=1): #TODO Really need a better way to get defaults
    #Used for market making "Sell_side" level
    #initiailize variables we'll use later
    x = starMarket(venues, stock, account)
    placedBuys={}
    placedSells={}
    cash=0
    NaV=0

    while True: #TODO need to handle connection exceptions
        #First compute how many outstanding buys and sells we have
        outstandingBuys=0
        for i in placedBuys.keys():
            outstandingBuys+=placedBuys[i][1]
        outstandingSells=0
        for i in placedSells.keys():
            outstandingSells+=placedSells[i][1]
        #query to get the asks/bids, also implement some sort of logic to determine if prices are "reasonable", currently trying spread size v price

        while (x.histAskPrice==0 or x.histBidPrice==0):
            for i in range(100):
                x.updatePriceStats()
                time.sleep(.1)
                print(i,'hi')
            print(x.histAskPrice,x.histBidPrice)
        while True:
            try: #Consider replacing with some sort of "get" for the ask
                x.updatePriceStats()
                quote=x.quoteStock()
                ask=quote.get('ask', quote.get('bid',x.histBidPrice)*profPercent*1.01) #Implementing some defaults for if only asks or only bids are available
                bid=quote.get('bid', quote.get('ask',x.histAskPrice)*(1/profPercent)*.99)
                spread=ask-bid
                spreadPerc=1+spread/bid #basing off of bid as that's how we're deciding what to buy
                lowOppAdj=lowOpp-(adjFactor*currentStocks/1000)
                highOppAdj=highOpp-(adjFactor*currentStocks/1000)
                #If there's a good spread then buy AND sell
                if spreadPerc>profPercent and (outstandingBuys+currentStocks<800) and currentStocks-outstandingSells>-800:
                    x.smartOrder(bid,buyMargin,'buy',volModifier,quote,placedBuys)
                    x.smartOrder(ask,sellMargin,'sell',volModifier,quote,placedSells)
                    print('Margin buy, placed Buys are ' +str(placedBuys) + ' placed sells are ' + str(placedSells))
                #if things are cheep then buy
                if  (bid<lowOppAdj*x.histBidPrice or ask<lowOppAdj*x.histAskPrice) and outstandingBuys+currentStocks<800:
                    x.smartOrder(bid, buyMargin, 'buy', volModifier, quote, placedBuys)
                    print('Cheap buy, placed Buys are ' + str(placedBuys))

                #if things are expensive then buy
                if (bid>highOppAdj*x.histAskPrice or ask>highOppAdj*x.histAskPrice) and currentStocks-outstandingSells>-800:
                    x.smartOrder(ask, sellMargin, 'sell', volModifier, quote, placedSells)
                    print('expensive sell, placed sells are ' +str(placedSells))
                # query current outstanding sells to see if we can remove then and remove them from volume, also see if we want to adjust how much money we've made
                #TODO Try to get this so I just make on request to get all my orders and then loop from that
                #query current outstanding buys to see if we can remove them and add the volume, possibly also keep a price avg of what you've bought
                    #Currently assuming that all orders are either completely filled or not filled at all, will see if it bites me
                for i in placedBuys.keys():
                    print(i, placedBuys[i])
                    status=x.orderStatus(i)
                    print(status)
                    if status['open'] == False:
                        print('bought order '+str(i)+' for a price of ' + str(placedBuys[i][0]) + ' and a volume of ' + str(placedBuys[i][1]))
                        volume=placedBuys[i][1]
                        currentStocks+=volume
                        cash-=volume*placedBuys[i][0]
                        placedBuys.pop(i)
                for i in placedSells.keys():
                    print(i, placedSells[i])
                    status=x.orderStatus(i)
                    print(status)
                    if status['open'] == False:
                        print('Sold order ' + str(i) + ' for a price of ' + str(placedSells[i][0]) + ' and a volume of ' + str(placedSells[i][1]))
                        volume=placedSells[i][1]
                        currentStocks-=volume
                        cash += volume * placedBuys[i][0]
                        placedSells.pop(i)
            except Exception as e: #TODO want a better way to handle connection and key error errors
                print(e)
                time.sleep(.2)
                # TODO Cancel any of my orders that have gotten too out of price range to keep them from filling up the buy/sell volume
            NaVstocks=currentStocks*quote['last']
            NaV=NaVstocks+cash
            print('cash is '+str(cash)+' buys are '+str(outstandingBuys)+' sells are '+str(outstandingSells),' current stocks are '+str(currentStocks) + ' NavStocks is ' + str(NaVstocks) + ' NaV ' + str(NaV))
            # print('historical sells are ' + str(x.histAskPrice) + 'historical buys are ' + str(x.histBidPrice), 'hist sell avg vol is ' + str(x.histAskAvgVol) + ' hist buy avg vol is ' +str(x.histBidAvgVol))
            time.sleep(.01)

    #Let's construct a loop that's always running

account = 'LPK97619919'
venues = 'LHBTEX'
stock = 'IEGH'
x = starMarket(venues, stock, account)
stealTrain(1.001,.99990,1.00005,10,.98,1.02,currentStocks=0)
# runTrain(938)
