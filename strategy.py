import talib
import numpy as np


price_data = np.array([], dtype=float)
hodl_assets = []
prev_rsi, profit = 0, 0


class Asset:
    def __init__(self, price, time, qty):
        self.price = price
        self.time = time
        self.qty = qty


class Strategy:
    def __init__(self, deposit, rsi_period, take_profit):
        self.deposit = deposit
        self.rsi_period = rsi_period
        self.take_profit = take_profit

    def is_sell_by_takeprofit(self, buy_price, sell_price):
        return (sell_price - buy_price) / buy_price * 100 >= self.take_profit

    def is_sell_by_time(self, open_time, current_time):
        return (current_time - open_time).total_seconds() // 3600 >= 24

    def try_buy(self, balance, time, price, create_buy_order):
        global f, hodl_assets, price_data, prev_rsi

        price_data = np.append(price_data, price)
        rsi = talib.RSI(price_data, timeperiod=self.rsi_period)
        # print('RSI %s' % rsi[-1])

        if len(price_data) > self.rsi_period:
            price_data = price_data[-self.rsi_period:]

        total_price = 0
        if prev_rsi >= 30 and rsi[-1] < 30:
            # print('%s - OVERSOLD! PRICE: %f$\n' % (time.strftime("%Y-%m-%d %H:%M"), price))
            # f.write('%s - OVERSOLD! PRICE: %f$\n' % (time.strftime("%Y-%m-%d %H:%M"), price))

            qty = "{:.8F}".format(round((self.deposit / price) / 4, 1))
            if balance >= float(qty)*price:
                try:
                    # print('BUY %f$ x %s\n' % (price, qty))
                    # f.write('BUY %f$ x %s\n' % (price, qty))
                    buy_order = create_buy_order(price, qty)
                    # print('BUY ORDER %s' % buy_order)
                    # f.write('BUY ORDER %s\n' % buy_order)
                    hodl_assets.append(Asset(price, time, qty))
                    total_price = float(qty)*price
                except Exception as e:
                    print(e)

        prev_rsi = rsi[-1]

        return total_price

    def try_sell(self, time, price, create_sell_order):
        global f, hodl_assets, profit

        _hodl_assets = []
        total_price = 0

        for (j, asset) in enumerate(hodl_assets):
            purchase_price = asset.price * float(asset.qty)
            selling_price = price * float(asset.qty)
            if self.is_sell_by_time(asset.time, time):
                try:
                    # print('%s - SELL BY TIME %f$ x %s\n' % (time.strftime("%Y-%m-%d %H:%M"), price, asset.qty))
                    # f.write('%s - SELL BY TIME %f$ x %s\n' % (time.strftime("%Y-%m-%d %H:%M"), price, asset.qty))
                    sell_order = create_sell_order(price, asset.qty)
                    # print('SELL ORDER %s' % sell_order)
                    # f.write('SELL ORDER %s\n' % sell_order)
                    profit += selling_price - purchase_price
                    total_price += selling_price
                except Exception as e:
                    print(e)
            elif self.is_sell_by_takeprofit(asset.price, price):
                try:
                    # print('%s - SELL BY TAKE PROFIT %f$ x %s\n' % (time.strftime("%Y-%m-%d %H:%M"), price, asset.qty))
                    # f.write('%s - SELL BY TAKE PROFIT %f$ x %s\n' % (time.strftime("%Y-%m-%d %H:%M"), price, asset.qty))
                    sell_order = create_sell_order(price, asset.qty)
                    # print('SELL ORDER %s' % sell_order)
                    # f.write('SELL ORDER %s\n' % sell_order)
                    profit += selling_price - purchase_price
                    total_price += selling_price
                except Exception as e:
                    print(e)
            else:
                _hodl_assets.append(asset)

        hodl_assets = _hodl_assets

        # print('HODL ASSETS: %s' % hodl_assets)
        # print('PROFIT: %f' % profit)
        # f.write('PROFIT: %f\n' % profit)

        # f.flush()

        return total_price
