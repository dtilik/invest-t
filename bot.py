import logging
from datetime import datetime, timedelta
import pandas as pd
from tinkoff.invest import Client, CandleInterval, OrderDirection, OrderType
from tinkoff.invest.utils import now
from tinkoff.invest.constants import INVEST_GRPC_API, INVEST_GRPC_API_SANDBOX

import config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("trading_bot.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self):
        self.token = config.TINKOFF_TOKEN
        self.sandbox_mode = config.SANDBOX_MODE
        self.ticker = config.TICKER
        self.target = INVEST_GRPC_API_SANDBOX if self.sandbox_mode else INVEST_GRPC_API
        self.figi = None
        self.account_id = None
        
    def run(self):
        """Main bot execution method"""
        logger.info("Starting trading bot")
        logger.info(f"Running in {'SANDBOX' if self.sandbox_mode else 'PRODUCTION'} mode")
        
        if not self.token:
            logger.error("Tinkoff API token not found. Check your .env file.")
            return
        
        with Client(self.token, target=self.target) as client:
            # Get accounts
            accounts = client.users.get_accounts()
            if not accounts.accounts:
                logger.error("No accounts found")
                return
                
            self.account_id = accounts.accounts[0].id
            logger.info(f"Using account: {self.account_id}")
            
            # Get instrument FIGI (Financial Instrument Global Identifier)
            instruments = client.instruments.find_instrument(query=self.ticker)
            if not instruments.instruments:
                logger.error(f"Instrument {self.ticker} not found")
                return
                
            self.figi = instruments.instruments[0].figi
            logger.info(f"Found instrument {self.ticker} with FIGI {self.figi}")
            
            # Get historical data
            candles = self.get_historical_data(client)
            if not candles:
                return
            
            # Analyze data and make trading decisions
            signal = self.analyze_data(candles)
            
            # Execute trades based on analysis
            if signal > 0:
                self.place_buy_order(client)
            elif signal < 0:
                self.place_sell_order(client)
            else:
                logger.info("No trading signal detected")
    
    def get_historical_data(self, client):
        """Get historical candle data"""
        try:
            logger.info(f"Getting historical data for {self.ticker}")
            
            # Calculate time range for historical data
            to_time = now()
            from_time = to_time - timedelta(days=1)
            
            # Set candle interval based on config
            interval_map = {
                "1m": CandleInterval.CANDLE_INTERVAL_1_MIN,
                "5m": CandleInterval.CANDLE_INTERVAL_5_MIN,
                "15m": CandleInterval.CANDLE_INTERVAL_15_MIN,
                "1h": CandleInterval.CANDLE_INTERVAL_HOUR
            }
            interval = interval_map.get(config.CANDLE_INTERVAL, CandleInterval.CANDLE_INTERVAL_1_MIN)
            
            # Request candles
            candles_response = client.market_data.get_candles(
                figi=self.figi,
                from_=from_time,
                to=to_time,
                interval=interval
            )
            
            # Convert to pandas DataFrame for analysis
            candle_data = []
            for candle in candles_response.candles:
                candle_data.append({
                    "time": candle.time,
                    "open": float(candle.open.units) + float(candle.open.nano) / 1e9,
                    "high": float(candle.high.units) + float(candle.high.nano) / 1e9,
                    "low": float(candle.low.units) + float(candle.low.nano) / 1e9,
                    "close": float(candle.close.units) + float(candle.close.nano) / 1e9,
                    "volume": candle.volume
                })
            
            df = pd.DataFrame(candle_data)
            logger.info(f"Received {len(df)} candles")
            return df
        
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return None
    
    def analyze_data(self, df):
        """Analyze data and generate trading signals"""
        if len(df) < config.LOOKBACK_PERIOD:
            logger.warning(f"Not enough data for analysis. Need {config.LOOKBACK_PERIOD} periods, got {len(df)}")
            return 0
        
        # Calculate returns
        df['returns'] = df['close'].pct_change()
        
        # Implement simple momentum strategy
        if config.STRATEGY == "simple_momentum":
            # Calculate momentum (sum of returns over lookback period)
            momentum = df['returns'].iloc[-config.LOOKBACK_PERIOD:].sum()
            
            if momentum > config.BUY_THRESHOLD:
                logger.info(f"BUY signal: momentum {momentum:.2%} > threshold {config.BUY_THRESHOLD:.2%}")
                return 1
            elif momentum < -config.SELL_THRESHOLD:
                logger.info(f"SELL signal: momentum {momentum:.2%} < threshold {-config.SELL_THRESHOLD:.2%}")
                return -1
            else:
                return 0
        
        # Placeholder for other strategies
        elif config.STRATEGY == "mean_reversion":
            # Implement mean reversion strategy
            return 0
        
        return 0
    
    def place_buy_order(self, client):
        """Place a buy order"""
        try:
            # Get portfolio to determine cash available
            portfolio = client.operations.get_portfolio(account_id=self.account_id)
            
            # Get current price
            last_price_response = client.market_data.get_last_prices(figi=[self.figi])
            if not last_price_response.last_prices:
                logger.error("Could not get current price")
                return
                
            last_price = float(last_price_response.last_prices[0].price.units) + \
                        float(last_price_response.last_prices[0].price.nano) / 1e9
            
            # Calculate quantity to buy
            cash = sum(position.current_price.units for position in portfolio.positions 
                      if position.instrument_type == "currency")
            
            order_amount = cash * config.POSITION_SIZE
            quantity = int(order_amount / last_price)
            
            if quantity <= 0:
                logger.warning("Insufficient funds for buy order")
                return
            
            # Place order
            if self.sandbox_mode:
                response = client.sandbox.post_sandbox_order(
                    figi=self.figi,
                    quantity=quantity,
                    direction=OrderDirection.ORDER_DIRECTION_BUY,
                    account_id=self.account_id,
                    order_type=OrderType.ORDER_TYPE_MARKET
                )
            else:
                response = client.orders.post_order(
                    figi=self.figi,
                    quantity=quantity,
                    direction=OrderDirection.ORDER_DIRECTION_BUY,
                    account_id=self.account_id,
                    order_type=OrderType.ORDER_TYPE_MARKET
                )
            
            logger.info(f"Buy order placed: {quantity} shares at ~{last_price}")
            logger.info(f"Order ID: {response.order_id}")
            
        except Exception as e:
            logger.error(f"Error placing buy order: {e}")
    
    def place_sell_order(self, client):
        """Place a sell order"""
        try:
            # Get positions to determine shares available
            positions = client.operations.get_positions(account_id=self.account_id)
            
            # Find position for our instrument
            quantity = 0
            for position in positions.securities:
                if position.figi == self.figi:
                    quantity = position.balance
                    break
            
            if quantity <= 0:
                logger.warning("No shares to sell")
                return
            
            # Place order
            if self.sandbox_mode:
                response = client.sandbox.post_sandbox_order(
                    figi=self.figi,
                    quantity=quantity,
                    direction=OrderDirection.ORDER_DIRECTION_SELL,
                    account_id=self.account_id,
                    order_type=OrderType.ORDER_TYPE_MARKET
                )
            else:
                response = client.orders.post_order(
                    figi=self.figi,
                    quantity=quantity,
                    direction=OrderDirection.ORDER_DIRECTION_SELL,
                    account_id=self.account_id,
                    order_type=OrderType.ORDER_TYPE_MARKET
                )
            
            logger.info(f"Sell order placed: {quantity} shares")
            logger.info(f"Order ID: {response.order_id}")
            
        except Exception as e:
            logger.error(f"Error placing sell order: {e}")

if __name__ == "__main__":
    bot = TradingBot()
    bot.run()
