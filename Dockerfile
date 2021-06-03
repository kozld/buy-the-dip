FROM otassel/python-talib:latest

ARG BINANCE_API
ARG BINANCE_SECRET

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
ENV binance_api=${BINANCE_API}
ENV binance_secret=${BINANCE_SECRET}

# CMD [ "python", "binance_bot.py" ]
