import os
import argparse
import datetime
import strategy

from binance import Client, ThreadedWebsocketManager


# init
api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')

client, deposit, token_a, token_b, token_pair, rsi_period, take_profit = None, None, None, None, None, None, None
prev_time = datetime.datetime.today()

def create_buy_order(price, qty):
    return client.create_order(symbol=token_pair, side='BUY', type='MARKET', quantity=qty)

def create_sell_order(price, qty):
    return client.create_order(symbol=token_pair, side='SELL', type='MARKET', quantity=qty)

def use_strategy(strategy):
    def handle_socket_message(msg):
        global prev_time
        time, price = None, None

        if msg['e'] != 'error':
            time = datetime.datetime.fromtimestamp(int(msg['E']) / 1000.0)
            price = float(msg['k']['c'])
            print('%s - PRICE %f' % (time.strftime("%Y-%m-%d %H:%M"), price))
        else:
            print('ERROR %s' % msg['e'])

        if (time - prev_time).total_seconds() // 60 >= 1:
            balance = float(client.get_asset_balance(asset=token_b)['free'])
            strategy.try_buy(balance, time, price, create_buy_order)
        prev_time = time

        strategy.try_sell(time, price, create_sell_order)

    return handle_socket_message

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simple Binance Trading Bot.')

    parser.add_argument('--deposit', dest='deposit', required=True, help='deposit amount (required)')
    parser.add_argument('--tokenA', dest='token_a', default='DOGE', help='the first token in a pair (default: DOGE)')
    parser.add_argument('--tokenB', dest='token_b', default='USDT', help='the second token in a pair (default: USDT)')
    parser.add_argument('--period', dest='period', default=15, help='RSI period (default: 15)')
    parser.add_argument('--takeProfit', dest='take_profit', default=2, help='takeprofit percentage (default: 2)')
    parser.add_argument('--testnet', action='store_true')

    args = parser.parse_args()

    deposit = float(args.deposit)
    token_a = args.token_a
    token_b = args.token_b
    rsi_period = int(args.period)
    take_profit = float(args.take_profit)
    token_pair = '%s%s' % (token_a, token_b)

    print('=============================')
    print('DEPOSIT: %f' % deposit)
    print('TOKEN A: %s' % token_a)
    print('TOKEN B: %s' % token_b)
    print('RSI PERIOD: %d' % rsi_period)
    print('TAKE PROFIT: %f' % take_profit)
    print('=============================')

    client = Client(api_key=api_key, api_secret=api_secret, testnet=args.testnet)
    print(client.get_account())

    twm = ThreadedWebsocketManager()
    twm.start()

    s = strategy.Strategy(deposit, rsi_period, take_profit)

    twm.start_kline_socket(callback=use_strategy(s), symbol=token_pair)
