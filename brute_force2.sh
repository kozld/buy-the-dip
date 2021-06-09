#!/bin/bash

# ==================================
# This utility is under construction
# ==================================

FILENAMES=("DOGEUSDT-1m-2021-01.csv" "DOGEUSDT-1m-2021-02.csv" "DOGEUSDT-1m-2021-03.csv" "DOGEUSDT-1m-2021-04.csv" "DOGEUSDT-1m-2021-05.csv")
START=10
END=10

for FILENAME in ${FILENAMES[@]}; do

  best_rsi=$START
  best_profit=0

  for i in $(seq $START $END); do

    python history_bot.py -f ${FILENAME} --deposit 1000 --period $i --takeProfit 2 > /dev/null
    profit=$( tail -n 1 trade_report.txt | awk '{print $2}' )

    if [ $(echo "$profit > $best_profit" |bc -l) -eq 1 ]; then
      best_profit=$profit
      best_rsi=$i
    fi

  done

  echo "===================================="
  echo "[FILENAME]" $FILENAME
  echo "[BEST RSI]" $best_rsi
  echo "[BEST PROFIT]" $best_profit
  echo "===================================="

done
