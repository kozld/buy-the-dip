FROM otassel/python-talib:alpine

ARG BINANCE_API
ARG BINANCE_SECRET

RUN apk update
RUN apk add make automake gcc g++ subversion python3-dev
RUN pip3 install --upgrade setuptools

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
ENV binance_api=${BINANCE_API}
ENV binance_secret=${BINANCE_SECRET}

COPY . .

CMD [ "python3", "binance_bot.py" ]
