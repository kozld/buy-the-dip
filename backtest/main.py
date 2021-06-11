import csv
import datetime

from argparse import ArgumentParser
from strategy import buy_the_dip
from store import redis_store

log, time_frame = None, None


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
        buy_value = 0

        # check possible to buy every <time_frame> min
        if (time - prev_time).total_seconds() // 60 >= time_frame:
            buy_value = s.try_buy(balance, time, price, create_buy_order, redis_store)
            balance -= buy_value
            prev_time = time

        # check possible to sell every times
        sell_value = s.try_sell(time, price, create_sell_order, redis_store)
        balance += sell_value

        if buy_value > 0 or sell_value > 0:
            log.write('%s,%s,%s,%s\n' % (time, price, buy_value, sell_value))
            log.flush()

    return handle_message


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument('-f', '--file', dest='filename', required=True, help='CSV file with historical data (required)')
    parser.add_argument('-d', '--deposit', dest='deposit', required=True, help='deposit amount (required)')
    parser.add_argument('-p', '--period', dest='period', default=15, help='RSI period (default: 15)')
    parser.add_argument('-t', '--takeProfit', dest='take_profit', default=2, help='take profit percentage (default: 2)')
    parser.add_argument('-m', '--timeFrame', dest='time_frame', default=1, help='time frame in minutes (default: 1)')
    parser.add_argument('-o', '--timeOut', dest='timeout', default=1, help='timeout in hours (default: 24)')
    args = parser.parse_args()

    filename = args.filename
    deposit = float(args.deposit)
    rsi_period = int(args.period)
    take_profit = float(args.take_profit)
    time_frame = int(args.time_frame)
    timeout = int(args.timeout)

    log = open('%s_REPORT.txt' % filename, 'w')
    log.write('TIME,PRICE,BUY AMOUNT,SELL AMOUNT\n')

    s = buy_the_dip.Strategy(deposit, rsi_period, take_profit, timeout)
    history_bot = use_strategy(s)

    with open('%s' % filename, "r") as f_obj:
        reader = csv_reader(f_obj)

        for row in reader:
            t = datetime.datetime.fromtimestamp(int(row[0]) / 1000.0)
            p = float(row[4])
            history_bot(t, p)
            # time.sleep(1)

    log.write('\n======== SUMMARY PROFIT ========\n' +
              '%s' % s.profit)
    log.flush()
