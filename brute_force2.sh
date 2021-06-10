#!/bin/bash

RSI_START=2
RSI_END=20
FRAME_START=1
FRAME_END=5

best_profit=-9999
best_rsi=$RSI_START
best_frame=$FRAME_START

for rsi in $(seq $RSI_START $RSI_END); do

  for frame in $(seq $FRAME_START $FRAME_END); do

    profit=0

    for day in $(seq 1 30); do
      python history_bot.py -f "day_${day}.csv" --deposit 1000 --period $rsi --takeProfit 0.3 --timeFrame $frame > /dev/null
      tmp=$( tail -n 1 trade_report.txt | awk '{print $2}' )
      profit=$(echo "$profit + $tmp" |bc -l)
    done

    if [ $(echo "$profit > $best_profit" |bc -l) -eq 1 ]; then
      best_profit=$profit
      best_rsi=$rsi
      best_frame=$frame
    fi

  done

done

echo "===================================="
echo "[BEST PROFIT]" $best_profit
echo "[BEST RSI]" $best_rsi
echo "[BEST FRAME]" $best_frame
echo "===================================="
