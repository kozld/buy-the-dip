FROM otassel/python-talib:latest

ARG BINANCE_API
ARG BINANCE_SECRET

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
ENV binance_api=${BINANCE_API}
ENV binance_secret=${BINANCE_SECRET}

COPY . .

CMD [ "python3", "binance_bot.py" ]