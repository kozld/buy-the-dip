import talib
import numpy as np


price_data = np.array([], dtype=float)
prev_rsi = 0


class Asset:

    def __init__(self, price, time, qty):

        self.price = price
        self.time = time
        self.qty = qty


class Strategy:

    profit = 0

    def __init__(self, deposit, rsi_period, take_profit, timeout):

        self.deposit = deposit
        self.rsi_period = rsi_period
        self.take_profit = take_profit
        self.timeout = timeout

    def is_sell_by_takeprofit(self, buy_price, sell_price):

        return (sell_price - buy_price) / buy_price * 100 >= self.take_profit

    def is_sell_by_time(self, open_time, current_time):

        return (current_time - open_time).total_seconds() // 3600 >= self.timeout

    def try_buy(self, balance, time, price, buy_interface, store_interface):

        global price_data, prev_rsi
        assets = store_interface.get()

        price_data = np.append(price_data, price)
        rsi = talib.RSI(price_data, timeperiod=self.rsi_period)

        if len(price_data) > self.rsi_period:
            price_data = price_data[-self.rsi_period:]

        total_price = 0
        if prev_rsi >= 30 and rsi[-1] < 30:

            qty = "{:.8F}".format(round((self.deposit / price) / 4, 1))
            if balance >= float(qty)*price:
                try:
                    buy_order = buy_interface(price, qty)
                    assets.append(Asset(price, time, qty))
                    total_price = float(qty)*price
                except Exception as e:
                    print(e)

        store_interface.set(assets)
        prev_rsi = rsi[-1]

        return total_price

    def try_sell(self, time, price, sell_interface, store_interface):

        assets = store_interface.get()
        _assets = []

        total_price = 0
        for asset in assets:
            purchase_price = asset.price * float(asset.qty)
            selling_price = price * float(asset.qty)

            if self.is_sell_by_time(asset.time, time):
                try:
                    sell_order = sell_interface(price, asset.qty)
                    self.profit += selling_price - purchase_price
                    total_price += selling_price
                except Exception as e:
                    print(e)
            elif self.is_sell_by_takeprofit(asset.price, price):
                try:
                    sell_order = sell_interface(price, asset.qty)
                    self.profit += selling_price - purchase_price
                    total_price += selling_price
                except Exception as e:
                    print(e)
            else:
                _assets.append(asset)

        store_interface.set(_assets)

        return total_price
