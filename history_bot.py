import csv
import datetime
import strategy

from argparse import ArgumentParser


def csv_reader(file_obj):
    return csv.reader(file_obj)

def create_buy_order(price, qty):
    pass

def create_sell_order(price, qty):
    pass

def use_strategy(strategy):

    prev_time = datetime.datetime.today()
    balance = strategy.deposit

    def handle_message(time, price):

        nonlocal prev_time, balance
        if (time - prev_time).total_seconds() // 60 >= 1:
            balance += strategy.try_buy(balance, time, price, create_buy_order)
        prev_time = time

        balance += strategy.try_sell(time, price, create_sell_order)

    return handle_message

if __name__ == "__main__":

    data_dir = 'history-data'

    parser = ArgumentParser()
    parser.add_argument('-f', '--file', dest='filename', required=True, help='CSV file with historical data (required)')
    parser.add_argument('-d', '--deposit', dest='deposit', required=True, help='deposit amount (required)')
    parser.add_argument('-p', '--period', dest='period', default=15, help='RSI period (default: 15)')
    parser.add_argument('-t', '--takeProfit', dest='take_profit', default=2, help='takeprofit percentage (default: 2)')
    args = parser.parse_args()

    deposit = float(args.deposit)
    rsi_period = int(args.period)
    take_profit = float(args.take_profit)

    s = strategy.Strategy(deposit, rsi_period, take_profit)
    history_bot = use_strategy(s)

    with open('%s/%s' % (data_dir, args.filename), "r") as f_obj:
        reader = csv_reader(f_obj)

        for row in reader:
            time = datetime.datetime.fromtimestamp(int(row[0]) / 1000.0)
            price = float(row[4])
            history_bot(time, price)
