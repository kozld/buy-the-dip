#!/bin/bash

FILENAME="DOGEUSDT-1m-2021-05.csv"
num_lines=$(wc -l $FILENAME | awk '{print $1}')
count=$((num_lines / 30))

day=1
for from in $(seq 1 $count $num_lines); do

  for line in $(seq $from $((from + count))); do
    line="`sed -n ${line}p $FILENAME`"
    echo $line >> "day_${day}.csv"
  done
  day=$((day + 1))

done
