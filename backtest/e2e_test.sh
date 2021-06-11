#!/bin/bash

DIR="."

profit=0
rsi=5
timeframe=1
timeout=5

for day in $(seq 1 30); do
  python history_bot.py -f "${DIR}/day_${day}.csv" --deposit 1000 --period $rsi --takeProfit 0.3 --timeFrame $timeframe --timeOut $timeout > /dev/null
  tmp=$( tail -n 1 "${DIR}/day_${day}_REPORT.txt" | awk -F"," '{print $1}' )
  profit=$(echo "$profit + $tmp" |bc -l)

  if [ $(( day % 5 )) -eq 0 ]; then
    result=$(${DIR}/utils/brute_force.sh "day_${day}.csv" | tail -n 1)

    rsi=$(echo $result | awk -F"," '{print $2}')
    timeframe=$(echo $result | awk -F"," '{print $3}')
    timeout=$(echo $result | awk -F"," '{print $4}')
  fi
done

echo "PROFIT=${profit}"
