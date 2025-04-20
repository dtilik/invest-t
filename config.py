import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Tinkoff token from environment variable
TINKOFF_TOKEN = os.getenv("TINKOFF_TOKEN")

# Trading settings
SANDBOX_MODE = True  # Set to False for real trading
LOGGING_ENABLED = True

# Strategy parameters
STRATEGY = "simple_momentum"  # Options: simple_momentum, mean_reversion
TICKER = "SBER"  # Default ticker to trade
CANDLE_INTERVAL = "1m"  # 1m, 5m, 15m, 1h
LOOKBACK_PERIOD = 14  # Number of candles to analyze
BUY_THRESHOLD = 0.005  # 0.5% price increase to trigger buy
SELL_THRESHOLD = 0.005  # 0.5% price decrease to trigger sell
POSITION_SIZE = 0.1  # 10% of available funds per trade
