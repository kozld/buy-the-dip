# Binance Trading Bot

This is a simple trading bot for the Binance exchange.

## Usage

### Install dependencies:

```pip install -r requirements.txt```

### Rename the file .env.example:

```mv .env.example .env```

Open the resulting file and fill your data (api_key, api_secret).

### Bot launch:

```python binance_bot.py [-h] --deposit DEPOSIT [--tokenA TOKEN_A] [--tokenB TOKEN_B] [--period PERIOD] [--takeprofit TAKEPROFIT]```

```optional arguments:
  -h, --help              show this help message and exit
  --deposit DEPOSIT       deposit amount (required)
  --tokenA TOKEN_A        the first token in a pair (default: DOGE)
  --tokenB TOKEN_B        the second token in a pair (default: USDT)
  --period PERIOD         RSI period (default: 15)
  --takeprofit TAKEPROFIT takeprofit percentage (default: 2)
