"""
Main application for Tinkoff Invest Trading Bot
"""
import logging
import time
from datetime import datetime, timedelta
import argparse

from tinkoff.invest import Client, CandleInterval
from tinkoff.invest.utils import now
from tinkoff.invest.constants import INVEST_GRPC_API, INVEST_GRPC_API_SANDBOX

import config
from utils.helpers import convert_candles_to_dataframe
from strategies.momentum.momentum_strategy import MomentumStrategy
from strategies.mean_reversion.mean_reversion_strategy import MeanReversionStrategy

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("trading_bot.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self, strategy_name=None, ticker=None, interval=None, sandbox=None):
        # Override config with command line arguments if provided
        self.token = config.TINKOFF_TOKEN
        self.sandbox_mode = sandbox if sandbox is not None else config.SANDBOX_MODE
        self.ticker = ticker or config.TICKER
        self.candle_interval = interval or config.CANDLE_INTERVAL
        self.strategy_name = strategy_name or config.STRATEGY
        
        self.target = INVEST_GRPC_API_SANDBOX if self.sandbox_mode else INVEST_GRPC_API
        self.figi = None
        self.account_id = None
        self.strategy = self._initialize_strategy()

    def _initialize_strategy(self):
        """Initialize selected trading strategy"""
        strategy_params = {
            'lookback_period': config.LOOKBACK_PERIOD,
            'buy_threshold': config.BUY_THRESHOLD,
            'sell_threshold': config.SELL_THRESHOLD,
            'window': 20,  # For mean reversion
            'std_dev_threshold': 1.5  # For mean reversion
        }
        
        if self.strategy_name == "simple_momentum":
            return MomentumStrategy(strategy_params)
        elif self.strategy_name == "mean_reversion":
            return MeanReversionStrategy(strategy_params)
        else:
            logger.warning(f"Unknown strategy '{self.strategy_name}', defaulting to momentum")
            return MomentumStrategy(strategy_params)
        
    def run(self, continuous=False, interval_minutes=15):
        """
        Main bot execution method
        
        Args:
            continuous (bool): If True, run continuously with specified interval
            interval_minutes (int): Minutes between trading runs in continuous mode
        """
        logger.info("Starting trading bot")
        logger.info(f"Running in {'SANDBOX' if self.sandbox_mode else 'PRODUCTION'} mode")
        logger.info(f"Strategy: {self.strategy_name}")
        logger.info(f"Trading {self.ticker} with {self.candle_interval} candles")
        
        if not self.token:
            logger.error("Tinkoff API token not found. Check your .env file.")
            return
        
        # Run once or continuously based on parameter
        if continuous:
            logger.info(f"Running in continuous mode with {interval_minutes} minute interval")
            while True:
                self._execute_trading_cycle()
                logger.info(f"Waiting {interval_minutes} minutes until next trading cycle...")
                time.sleep(interval_minutes * 60)
        else:
            self._execute_trading_cycle()
    
    def _execute_trading_cycle(self):
        """Execute a single trading cycle"""
        try:
            with Client(self.token, target=self.target) as client:
                # Initialize account and instrument
                if not self._initialize_trading(client):
                    return
                
                # Get historical data
                candles = self._get_historical_data(client)
                if not candles or len(candles) == 0:
                    logger.warning("No candle data received, skipping trading cycle")
                    return
                
                # Analyze data using selected strategy
                signal = self.strategy.generate_signal(candles)
                
                # Execute trades based on analysis
                if signal > 0:
                    logger.info("BUY signal received")
                    self._place_buy_order(client)
                elif signal < 0:
                    logger.info("SELL signal received")
                    self._place_sell_order(client)
                else:
                    logger.info("No trading signal detected")
                
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}")
    
    def _initialize_trading(self, client):
        """Initialize account and get instrument information"""
        try:
            # Get accounts
            accounts = client.users.get_accounts()
            if not accounts.accounts:
                logger.error("No accounts found")
                return False
                
            self.account_id = accounts.accounts[0].id
            logger.info(f"Using account: {self.account_id}")
            
            # Get instrument FIGI
            instruments = client.instruments.find_instrument(query=self.ticker)
            if not instruments.instruments:
                logger.error(f"Instrument {self.ticker} not found")
                return False
                
            self.figi = instruments.instruments[0].figi
            instrument_name = instruments.instruments[0].name
            logger.info(f"Found instrument: {instrument_name} ({self.ticker}) with FIGI {self.figi}")
            
            # If in sandbox mode, ensure we have funds
            if self.sandbox_mode:
                self._ensure_sandbox_balance(client)
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing trading: {e}")
            return False
    
    def _ensure_sandbox_balance(self, client):
        """Ensure we have sufficient funds in sandbox mode"""
        try:
            # Get current balance
            portfolio = client.sandbox.get_sandbox_portfolio(account_id=self.account_id)
            positions = portfolio.positions
            
            # Check if we need to add funds
            has_sufficient_funds = False
            for position in positions:
                if position.instrument_type == "currency":
                    currency_position = float(position.quantity.units) + float(position.quantity.nano) / 1e9
                    if currency_position > 10000:  # Arbitrary threshold
                        has_sufficient_funds = True
                        break
            
            # Add sandbox balance if needed
            if not has_sufficient_funds:
                logger.info("Adding funds to sandbox account")
                client.sandbox.sandbox_pay_in(
                    account_id=self.account_id,
                    amount={"units": 100000, "nano": 0},
                )
                logger.info("Added 100,000 RUB to sandbox account")
                
        except Exception as e:
            logger.error(f"Error ensuring sandbox balance: {e}")
    
    def _get_historical_data(self, client):
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
            interval = interval_map.get(self.candle_interval, CandleInterval.CANDLE_INTERVAL_1_MIN)
            
            # Request candles
            candles_response = client.market_data.get_candles(
                figi=self.figi,
                from_=from_time,
                to=to_time,
                interval=interval
            )
            
            # Convert to pandas DataFrame for analysis
            df = convert_candles_to_dataframe(candles_response.candles)
            logger.info(f"Received {len(df)} candles")
            return df
        
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return None
    
    def _place_buy_order(self, client):
        """Place a buy order"""
        try:
            # Get portfolio to determine cash available
            if self.sandbox_mode:
                portfolio = client.sandbox.get_sandbox_portfolio(account_id=self.account_id)
            else:
                portfolio = client.operations.get_portfolio(account_id=self.account_id)
            
            # Get current price
            last_price_response = client.market_data.get_last_prices(figi=[self.figi])
            if not last_price_response.last_prices:
                logger.error("Could not get current price")
                return
                
            last_price = float(last_price_response.last_prices[0].price.units) + \
                        float(last_price_response.last_prices[0].price.nano) / 1e9
            
            # Calculate quantity to buy
            cash = 0
            for position in portfolio.positions:
                if position.instrument_type == "currency":
                    cash += float(position.quantity.units) + float(position.quantity.nano) / 1e9
            
            order_amount = cash * config.POSITION_SIZE
            quantity = int(order_amount / last_price)
            
            if quantity <= 0:
                logger.warning("Insufficient funds for buy order")
                return
            
            # Place order
            if self.sandbox_mode:
                order_response = client.sandbox.post_sandbox_order(
                    figi=self.figi,
                    quantity=quantity,
                    price=None,  # Market order
                    direction=1,  # Buy
                    account_id=self.account_id,
                    order_type=2  # Market order
                )
            else:
                order_response = client.orders.post_order(
                    figi=self.figi,
                    quantity=quantity,
                    price=None,  # Market order
                    direction=1,  # Buy
                    account_id=self.account_id,
                    order_type=2  # Market order
                )
            
            logger.info(f"Buy order placed: {quantity} shares at ~{last_price:.2f}")
            logger.info(f"Order ID: {order_response.order_id}")
            
        except Exception as e:
            logger.error(f"Error placing buy order: {e}")
    
    def _place_sell_order(self, client):
        """Place a sell order"""
        try:
            # Get positions to determine shares available
            if self.sandbox_mode:
                positions = client.sandbox.get_sandbox_positions(account_id=self.account_id)
            else:
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
                order_response = client.sandbox.post_sandbox_order(
                    figi=self.figi,
                    quantity=quantity,
                    price=None,  # Market order
                    direction=2,  # Sell
                    account_id=self.account_id,
                    order_type=2  # Market order
                )
            else:
                order_response = client.orders.post_order(
                    figi=self.figi,
                    quantity=quantity,
                    price=None,  # Market order
                    direction=2,  # Sell
                    account_id=self.account_id,
                    order_type=2  # Market order
                )
            
            logger.info(f"Sell order placed: {quantity} shares")
            logger.info(f"Order ID: {order_response.order_id}")
            
        except Exception as e:
            logger.error(f"Error placing sell order: {e}")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Tinkoff Invest Trading Bot')
    parser.add_argument('--strategy', type=str, choices=['simple_momentum', 'mean_reversion'],
                        help='Trading strategy to use')
    parser.add_argument('--ticker', type=str, help='Ticker symbol to trade')
    parser.add_argument('--interval', type=str, choices=['1m', '5m', '15m', '1h'],
                        help='Candle interval')
    parser.add_argument('--sandbox', action='store_true', help='Use sandbox mode')
    parser.add_argument('--continuous', action='store_true', help='Run continuously')
    parser.add_argument('--cycle-minutes', type=int, default=15,
                        help='Minutes between trading cycles in continuous mode')
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    bot = TradingBot(
        strategy_name=args.strategy,
        ticker=args.ticker,
        interval=args.interval,
        sandbox=args.sandbox if args.sandbox else None
    )
    
    bot.run(continuous=args.continuous, interval_minutes=args.cycle_minutes)
