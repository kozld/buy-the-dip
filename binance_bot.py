import os
import talib
import datetime
import numpy as np

from binance import Client, ThreadedWebsocketManager


class Asset:
    def __init__(self, price, time, qty):
        self.price = price
        self.time = time
        self.qty = qty


# init
DEPOSIT=10000
RSI_PERIOD=3
TAKE_PROFIT=2
api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')

client = Client(api_key=api_key, api_secret=api_secret, testnet=True)
f = open('trade-report.txt', 'w')
price_data = np.array([], dtype=float)
hodl_assets = []
prev_time = datetime.datetime.today()
prev_rsi = 0


def is_sell_by_takeprofit(buy_price, sell_price):
    return (sell_price - buy_price) / buy_price * 100 >= TAKE_PROFIT

def is_sell_by_time(open_time, current_time):
    return (current_time - open_time).total_seconds() // 3600 >= 5


def buy_the_dip(msg):
    global f, hodl_assets, price_data, prev_time, prev_rsi
    time, price = None, None

    if msg['e'] != 'error':
        time = datetime.datetime.fromtimestamp(int(msg['E']) / 1000.0)
        price = float(msg['k']['c'])
        print('%s - PRICE %f' % (time.strftime("%Y-%m-%d %H:%M"), price))
        #f.write('%s - PRICE %f\n' % (time.strftime("%Y-%m-%d %H:%M"), price))
    else:
        print('ERROR %s' % msg['e'])

    if (time - prev_time).total_seconds() // 60 >= 1:
        price_data = np.append(price_data, price)
        rsi = talib.RSI(price_data, timeperiod=RSI_PERIOD)
        print('RSI %s' % rsi[-1])
        #f.write('RSI %s\n' % rsi[-1])

        if len(price_data) > 3:
            price_data = price_data[-RSI_PERIOD:]

        if prev_rsi >= 30 and rsi[-1] < 30:
            print('%s - OVERSOLD! PRICE: %f$\n' % (time.strftime("%Y-%m-%d %H:%M"), price))
            f.write('%s - OVERSOLD! PRICE: %f$\n' % (time.strftime("%Y-%m-%d %H:%M"), price))

            balance = float(client.get_asset_balance(asset='USDT')['free'])
            #hodled_usd = reduce(lambda a, b: b.price * b.quantity, hodl_assets, 0)
            qty = round((DEPOSIT / price) / 4, 2)

            if balance >= qty*price:
                try:
                    print('BUY %f$ x %f\n' % (price, qty))
                    f.write('BUY %f$ x %f\n' % (price, qty))
                    buy_order = client.create_order(symbol='BNBUSDT', side='BUY', type='MARKET', quantity=qty)
                    print('BUY ORDER %s' % buy_order)
                    f.write('BUY ORDER %s\n' % buy_order)
                    hodl_assets.append(Asset(price, time, qty))
                except Exception as e:
                    print(e)

        prev_time = time
        prev_rsi = rsi[-1]

    _hodl_assets = []
    for (j, asset) in enumerate(hodl_assets):
        if is_sell_by_time(asset.time, time):
            try:
                sell_order = client.create_order(symbol='BNBUSDT', side='SELL', type='MARKET', quantity=asset.qty)
                print('%s - SELL BY TIME %f$ x %f\n' % (time.strftime("%Y-%m-%d %H:%M"), price, asset.qty))
                f.write('%s - SELL BY TIME %f$ x %f\n' % (time.strftime("%Y-%m-%d %H:%M"), price, asset.qty))
                print('SELL ORDER %s' % sell_order)
                f.write('SELL ORDER %s\n' % sell_order)
            except Exception as e:
                print(e)
        elif is_sell_by_takeprofit(asset.price, price):
            try:
                sell_order = client.create_order(symbol='BNBUSDT', side='SELL', type='MARKET', quantity=asset.qty)
                print('%s - SELL BY TAKE PROFIT %f$ x %f\n' % (time.strftime("%Y-%m-%d %H:%M"), price, asset.qty))
                f.write('%s - SELL BY TAKE PROFIT %f$ x %f\n' % (time.strftime("%Y-%m-%d %H:%M"), price, asset.qty))
                print('SELL ORDER %s' % sell_order)
                f.write('SELL ORDER %s\n' % sell_order)
            except Exception as e:
                print(e)
        else:
            _hodl_assets.append(asset)

    f.flush()
    hodl_assets = _hodl_assets
    print('HODL ASSETS: ', hodl_assets)


if __name__ == "__main__":
    print(client.get_account())

    twm = ThreadedWebsocketManager()
    twm.start()

    twm.start_kline_socket(callback=buy_the_dip, symbol='BNBUSDT')
