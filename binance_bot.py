import os
import talib
import argparse
import datetime
import numpy as np

from binance import Client, ThreadedWebsocketManager


# init
api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')
deposit, token_a, token_b, token_pair, rsi_period, takeprofit = None, None, None, None, None, None

client = None
f = open('trade-report.txt', 'w')
price_data = np.array([], dtype=float)
hodl_assets = []
prev_time = datetime.datetime.today()
prev_rsi = 0
profit = 0

class Asset:
    def __init__(self, price, time, qty):
        self.price = price
        self.time = time
        self.qty = qty


def is_sell_by_takeprofit(buy_price, sell_price):
    return (sell_price - buy_price) / buy_price * 100 >= takeprofit

def is_sell_by_time(open_time, current_time):
    return (current_time - open_time).total_seconds() // 3600 >= 5


def buy_the_dip(msg):
    global f, hodl_assets, price_data, prev_time, prev_rsi, profit
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
        rsi = talib.RSI(price_data, timeperiod=rsi_period)
        print('RSI %s' % rsi[-1])
        #f.write('RSI %s\n' % rsi[-1])

        if len(price_data) > 3:
            price_data = price_data[-rsi_period:]

        if prev_rsi >= 30 and rsi[-1] < 30:
            print('%s - OVERSOLD! PRICE: %f$\n' % (time.strftime("%Y-%m-%d %H:%M"), price))
            f.write('%s - OVERSOLD! PRICE: %f$\n' % (time.strftime("%Y-%m-%d %H:%M"), price))

            balance = float(client.get_asset_balance(asset=token_b)['free'])
            #hodled_usd = reduce(lambda a, b: b.price * b.quantity, hodl_assets, 0)
            qty = round((deposit / price) / 4, 2)

            if balance >= qty*price:
                try:
                    print('BUY %f$ x %f\n' % (price, qty))
                    f.write('BUY %f$ x %f\n' % (price, qty))
                    buy_order = client.create_order(symbol=token_pair, side='BUY', type='MARKET', quantity=qty)
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
                sell_order = client.create_order(symbol=token_pair, side='SELL', type='MARKET', quantity=asset.qty)
                print('%s - SELL BY TIME %f$ x %f\n' % (time.strftime("%Y-%m-%d %H:%M"), price, asset.qty))
                f.write('%s - SELL BY TIME %f$ x %f\n' % (time.strftime("%Y-%m-%d %H:%M"), price, asset.qty))
                print('SELL ORDER %s' % sell_order)
                f.write('SELL ORDER %s\n' % sell_order)
                profit += (price - asset.price) * asset.qty
            except Exception as e:
                print(e)
        elif is_sell_by_takeprofit(asset.price, price):
            try:
                sell_order = client.create_order(symbol=token_pair, side='SELL', type='MARKET', quantity=asset.qty)
                print('%s - SELL BY TAKE PROFIT %f$ x %f\n' % (time.strftime("%Y-%m-%d %H:%M"), price, asset.qty))
                f.write('%s - SELL BY TAKE PROFIT %f$ x %f\n' % (time.strftime("%Y-%m-%d %H:%M"), price, asset.qty))
                print('SELL ORDER %s' % sell_order)
                f.write('SELL ORDER %s\n' % sell_order)
                profit += (price - asset.price) * asset.qty
            except Exception as e:
                print(e)
        else:
            _hodl_assets.append(asset)

    f.flush()
    hodl_assets = _hodl_assets
    print('HODL ASSETS: ', hodl_assets)
    print('PROFIT: ', profit)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simple Binance Trading Bot.')

    parser.add_argument('--deposit', dest='deposit', required=True, help='deposit amount (required)')
    parser.add_argument('--tokenA', dest='token_a', default='DOGE', help='the first token in a pair (default: DOGE)')
    parser.add_argument('--tokenB', dest='token_b', default='USDT', help='the second token in a pair (default: USDT)')
    parser.add_argument('--period', dest='period', default=15, help='RSI period (default: 15)')
    parser.add_argument('--takeprofit', dest='takeprofit', default=2, help='takeprofit percentage (default: 2)')
    parser.add_argument('--testnet', action='store_true')

    args = parser.parse_args()

    deposit = float(args.deposit)
    token_a = args.token_a
    token_b = args.token_b
    rsi_period = int(args.period)
    takeprofit = float(args.takeprofit)
    token_pair = '%s%s' % (token_a, token_b)

    print('=============================')
    print('DEPOSIT: %f' % deposit)
    print('TOKEN A: %s' % token_a)
    print('TOKEN B: %s' % token_b)
    print('RSI PERIOD: %d' % rsi_period)
    print('TAKE PROFIT: %f' % takeprofit)
    print('=============================')

    client = Client(api_key=api_key, api_secret=api_secret, testnet=args.testnet)
    print(client.get_account())

    twm = ThreadedWebsocketManager()
    twm.start()

    twm.start_kline_socket(callback=buy_the_dip, symbol=token_pair)
