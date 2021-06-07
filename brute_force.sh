#!/bin/bash

# ==================================
# This utility is under construction
# ==================================

FILENAME="DOGEUSDT-1m-2021-05.csv"
START=2
END=30

best_profit=0
best_rsi=$START
for i in $(seq $START $END); do
  python history_bot.py -f ${FILENAME} --deposit 1000 --period $i
  profit=$( tail -n 1 trade_report.txt | awk '{print $2}' )
  if [ $(echo "$profit > $best_profit" |bc -l) -eq 1 ]; then
    best_profit=$profit
    best_rsi=$i
  fi
done

echo "===================================="
echo $best_rsi
echo $best_profit
echo "===================================="