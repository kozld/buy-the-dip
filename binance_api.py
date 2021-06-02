import os
import talib
import datetime
import time as t
import numpy as np

from binance import Client, ThreadedWebsocketManager


class Asset:
    def __init__(self, price, time, qty):
        self.price = price
        self.time = time
        self.qty = qty


# init
DEPOSIT=500
RSI_PERIOD=3
TAKE_PROFIT=2
api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')

client = Client(api_key=api_key, api_secret=api_secret, testnet=True)
f = open('trade-report.txt', 'w')
price_data = np.array([], dtype=float)
hodl_assets = []


def is_sell_by_takeprofit(buy_price, sell_price):
    return (sell_price - buy_price) / buy_price * 100 >= TAKE_PROFIT

def is_sell_by_time(open_time, current_time):
    return (current_time - open_time).total_seconds() // 3600 >= 5


def buy_the_dip(msg):
    global hodl_assets, price_data
    time, price = None, None

    if msg['e'] != 'error':
        time = datetime.datetime.fromtimestamp(int(msg['E']) / 1000.0)
        price = float(msg['k']['c'])
        print('%s - PRICE %f' % (time.strftime("%Y-%m-%d %H:%M"), price))
        price_data = np.append(price_data, price)
    else:
        print('ERROR %s' % msg['e'])

    rsi = talib.RSI(price_data, timeperiod=RSI_PERIOD)
    print('RSI %s' % rsi[-1])

    if len(price_data) > 3:
        price_data = price_data[-3:]

    if len(rsi) > 2 and rsi[-2] >= 30 and rsi[-1] < 30:
        print('OVERSOLD! PRICE: %f$\n' % price)

        balance = client.get_asset_balance(asset='BNB')
        qty = (DEPOSIT // price) // 4

        if balance + qty*price <= DEPOSIT:
            try:
                print('BUY %f$ x %d\n' % (price, qty))
                buy_order = client.create_test_order(symbol='BNBBTC', side='BUY', type='MARKET', quantity=qty)
                print('BUY ORDER %s' % buy_order)
                hodl_assets.append(Asset(price, time, qty))
            except Exception as e:
                print(e)

    _hodl_assets = []
    for (j, asset) in enumerate(hodl_assets):
        if is_sell_by_time(asset.time, time):
            try:
                sell_order = client.create_test_order(symbol='BNBBTC', side='SELL', type='MARKET', quantity=asset.qty)
                print('SELL BY TIME %f$ x %d\n' % (price, asset.qty))
                print('SELL ORDER %s' % sell_order)
            except Exception as e:
                print(e)
        elif is_sell_by_takeprofit(asset.price, price):
            try:
                sell_order = client.create_test_order(symbol='BNBBTC', side='SELL', type='MARKET', quantity=asset.qty)
                print('SELL BY TAKE PROFIT %f$ x %d\n' % (price, asset.qty))
                print('SELL ORDER %s' % sell_order)
            except Exception as e:
                print(e)
        else:
            _hodl_assets.append(asset)

    hodl_assets = _hodl_assets
    print('HODL ASSETS: ', hodl_assets)


if __name__ == "__main__":
    print(client.get_account())

    twm = ThreadedWebsocketManager()
    twm.start()

    twm.start_kline_socket(callback=buy_the_dip, symbol='BNBBTC')
