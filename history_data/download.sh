#!/bin/bash

symbols=("DOGEUSDT")
intervals=("1m")
years=("2021")
months=(01 02 03 04 05)

baseurl="https://data.binance.vision/data/spot/monthly/klines"

for symbol in ${symbols[@]}; do
  for interval in ${intervals[@]}; do
    for year in ${years[@]}; do
      for month in ${months[@]}; do
        filename="${symbol}-${interval}-${year}-${month}"

        if [ ! -d "${filename}.zip" ]; then
          url="${baseurl}/${symbol}/${interval}/${filename}.zip"
          response=$(wget --no-check-certificate --server-response -q ${url} 2>&1 | awk 'NR==1{print $2}')
          if [ ${response} == '403' ]; then
            echo "File not exist: ${url}" 
          else
            echo "downloaded: ${url}"
          fi
        fi

        if [ ! -f "${filename}.csv" ]; then
          tar -xvf ${filename}.zip
        fi

      done
    done
  done
done