#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
HISTORY_DIR="history"

if [ $# -lt 1 ]; then
  echo "expected one argument"
  exit 1
fi

FILENAME=$1
if [ ! -f "${HISTORY_DIR}/${FILENAME}" ]; then
  echo "file not found"
  exit 1
fi

# init
RSI_START=2
RSI_END=10
FRAME_START=1
FRAME_END=10
TIMEOUT_START=4
TIMEOUT_END=24
TIMEOUT_STEP=4

best_profit=-9999
best_rsi=$RSI_START
best_frame=$FRAME_START
best_timeout=$TIMEOUT_START

for rsi in $(seq $RSI_START $RSI_END); do

  for frame in $(seq $FRAME_START $FRAME_END); do

    for timeout in $(seq $TIMEOUT_START $TIMEOUT_STEP $TIMEOUT_END); do

      echo "[RSI]" $rsi
      echo "[FRAME]" $frame
      echo "[TIMEOUT]" $timeout

      profit=0

      python ./fake.py -f "${HISTORY_DIR}/${FILENAME}" --deposit 1000 --period $rsi --takeProfit 0.3 --timeFrame $frame --timeOut $timeout
      profit=$( tail -n 1 "${HISTORY_DIR}/${FILENAME}_REPORT.txt" | awk -F"," '{print $1}' )

      if [ $(echo "$profit > $best_profit" |bc -l) -eq 1 ]; then
        best_profit=$profit
        best_rsi=$rsi
        best_frame=$frame
        best_timeout=$timeout
      fi

    done

  done

done

echo "PROFIT,RSI,TIMEFRAME,TIMEOUT"
echo "${best_profit},${best_rsi},${best_frame},${best_timeout}"
