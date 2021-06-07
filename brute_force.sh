#!/bin/bash

# ==================================
# This utility is under construction
# ==================================

FILENAMES=("DOGEUSDT-5m-2021-01.csv" "DOGEUSDT-5m-2021-02.csv" "DOGEUSDT-5m-2021-03.csv" "DOGEUSDT-5m-2021-04.csv" "DOGEUSDT-5m-2021-05.csv")
START=2
END=30

best_rsi=$START
best_profit=0

for i in $(seq $START $END); do

  profit=0
  for FILENAME in ${FILENAMES[@]}; do

    python history_bot.py -f ${FILENAME} --deposit 1000 --period $i > /dev/null
    tmp=$( tail -n 1 trade_report.txt | awk '{print $2}' )
    profit=$(echo "$profit + $tmp" |bc -l)
  done

  if [ $(echo "$profit > $best_profit" |bc -l) -eq 1 ]; then
    best_profit=$profit
    best_rsi=$i
  fi

done

echo "===================================="
echo "[BEST RSI]" $best_rsi
echo "[BEST PROFIT]" $best_profit
echo "===================================="
