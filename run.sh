#!/bin/bash

./clean.sh

symbols=("DOGEUSDT")
intervals=("1m")
years=("2019" "2020" "2021")
months=(01 02 03 04 05 06 07 08 09 10 11 12)

baseurl="https://data.binance.vision/data/spot/monthly/klines"

for symbol in ${symbols[@]}; do
  for interval in ${intervals[@]}; do
    for year in ${years[@]}; do
      for month in ${months[@]}; do
        filename="${symbol}-${interval}-${year}-${month}"

        if [ ! -d "klines/${filename}.zip" ]; then
          url="${baseurl}/${symbol}/${interval}/${filename}.zip"
          response=$(wget --no-check-certificate -P klines --server-response -q ${url} 2>&1 | awk 'NR==1{print $2}')
          if [ ${response} == '403' ]; then
            echo "File not exist: ${url}" 
          else
            echo "downloaded: ${url}"
          fi
        fi

        if [ ! -f "klines/${filename}.csv" ]; then
          tar -xvf klines/${filename}.zip -C klines
        fi

        python ./buy_the_dip.py -f "${filename}.csv"
      done
    done
  done
done