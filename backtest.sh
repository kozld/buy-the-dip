#!/bin/bash

HISTORY_DIR="history"

profit=0
rsi=5
timeframe=1
timeout=5

for day in $(seq 1 30); do
  echo "Day ${day}..."
  python fake.py -f "${HISTORY_DIR}/day_${day}.csv" --deposit 1000 --period $rsi --takeProfit 0.3 --timeFrame $timeframe --timeOut $timeout > /dev/null
  tmp=$( tail -n 1 "${HISTORY_DIR}/day_${day}.csv_REPORT.txt" | awk -F"," '{print $1}' )
  profit=$(echo "$profit + $tmp" |bc -l)

  echo "Day profit: ${tmp}$"
  echo "Total profit: ${profit}$"

  #if [ $(( day % 5 )) -eq 0 ]; then
  if [ $(echo "$tmp < 5" |bc -l) -eq 1 ]; then
    result=$(./utils/brute_force.sh "day_${day}.csv" | tail -n 1)

    rsi=$(echo $result | awk -F"," '{print $2}')
    timeframe=$(echo $result | awk -F"," '{print $3}')
    timeout=$(echo $result | awk -F"," '{print $4}')
  fi
done

echo "PROFIT: ${profit}"
