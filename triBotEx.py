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
    items_file = open('data/items.txt', 'r')
    prices_file = open('prices.txt', 'w')
    for line in items_file:
        line = line.replace('\n', '')
        prices_file.write(line + ':' + str(get_price(get_id(line, names))) + '\n')
    items_file.close()
    prices_file.close()


main()