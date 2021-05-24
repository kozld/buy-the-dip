# -*- encoding: utf-8 -*-

import datetime
import numpy as np
import talib
import csv

from argparse import ArgumentParser
from random import seed
from random import random
from matplotlib import pyplot
from functools import reduce


RSI_PERIOD=3
TAKE_PROFIT=2
DEPOSIT=3000

class Asset:
	def __init__(self, price, time, qty):
		self.price = price
		self.time = time
		self.quantity = qty

def is_sell_by_takeprofit(buy_price, sell_price):
	return (sell_price - buy_price) / buy_price * 100 >= TAKE_PROFIT

def is_sell_by_time(open_time, current_time):
	return (current_time - open_time).total_seconds() // 3600 >= 5

def buy_the_dip(data_binance_format, log_file):
	profit = 0
	hodl_assets = []

	for (i, row) in enumerate(data_binance_format):
		current_time = datetime.datetime.fromtimestamp(int(row[0]) / 1000.0)
		close_price = float(row[4])

		if close_price <= 0:
			continue

		if rsi[i-1] >= 30 and rsi[i] < 30:
			log_file.write('oversold! price: %f$\n' % close_price)
			log_file.write('buy %f$\n' % close_price)
			qty = (DEPOSIT // close_price) // 4
			hodled_usd = reduce(lambda a, b: b.price * b.quantity, hodl_assets, 0)
			if hodled_usd + qty*close_price <= DEPOSIT:
				hodl_assets.append(Asset(close_price, current_time, qty))

		_hodl_assets = []
		for (j, asset) in enumerate(hodl_assets):
			if is_sell_by_time(asset.time, current_time) or i == len(data_binance_format)-1:
				log_file.write('sell by time %f$\n' % close_price)
				profit += (close_price - asset.price) * asset.quantity
			elif is_sell_by_takeprofit(asset.price, close_price):
				log_file.write('sell by takeprofit %f$\n' % close_price)
				profit += (close_price - asset.price) * asset.quantity
			else:
				_hodl_assets.append(asset)

		hodl_assets = _hodl_assets

	return profit

def csv_reader(file_obj):
    return csv.reader(file_obj)

if __name__ == "__main__":

	klines_dir = 'klines'
	reports_dir = 'reports'

	parser = ArgumentParser()
	parser.add_argument("-f", "--file", dest="filename", help="CSV file with historical price data")
	args = parser.parse_args()

	price_data = np.array([], dtype=float)
	with open('%s/%s' % (klines_dir, args.filename), "r") as f_obj:
		reader = csv_reader(f_obj)

		for row in reader:
			price_data = np.append(price_data, float(row[4]))

	rsi = talib.RSI(price_data, timeperiod=RSI_PERIOD)

	reader = list(csv_reader(open('%s/%s' % (klines_dir, args.filename), "r")))
	f = open('%s/%s-report.txt' % (reports_dir, args.filename), 'w')

	profit = buy_the_dip(reader, f)

	f.write('profit: %f$' % profit)
	f.close()
