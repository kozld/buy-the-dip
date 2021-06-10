import csv
import time
import datetime
import strategy

from argparse import ArgumentParser


time_frame = None


def csv_reader(file_obj):
    return csv.reader(file_obj)


def create_buy_order(price, qty):
    pass


def create_sell_order(price, qty):
    pass


def use_strategy(s):

    prev_time = datetime.datetime.fromtimestamp(0)
    balance = s.deposit

    def handle_message(time, price):

        nonlocal prev_time, balance

        # check possible to buy every <time_frame> min
        if (time - prev_time).total_seconds() // 60 >= time_frame:
            balance -= s.try_buy(balance, time, price, create_buy_order)
            prev_time = time

        # check possible to sell every times
        balance += s.try_sell(time, price, create_sell_order)

    return handle_message


if __name__ == "__main__":

    data_dir = 'history_data'

    parser = ArgumentParser()
    parser.add_argument('-f', '--file', dest='filename', required=True, help='CSV file with historical data (required)')
    parser.add_argument('-d', '--deposit', dest='deposit', required=True, help='deposit amount (required)')
    parser.add_argument('-p', '--period', dest='period', default=15, help='RSI period (default: 15)')
    parser.add_argument('-t', '--takeProfit', dest='take_profit', default=2, help='takeprofit percentage (default: 2)')
    parser.add_argument('-m', '--timeFrame', dest='time_frame', default=1, help='time frame in minutes (default: 1)')
    args = parser.parse_args()

    deposit = float(args.deposit)
    rsi_period = int(args.period)
    take_profit = float(args.take_profit)
    time_frame = int(args.time_frame)

    s = strategy.Strategy(deposit, rsi_period, take_profit)
    history_bot = use_strategy(s)

    with open('%s/%s' % (data_dir, args.filename), "r") as f_obj:
        reader = csv_reader(f_obj)

        for row in reader:
            t = datetime.datetime.fromtimestamp(int(row[0]) / 1000.0)
            p = float(row[4])
            history_bot(t, p)
            # time.sleep(1)
