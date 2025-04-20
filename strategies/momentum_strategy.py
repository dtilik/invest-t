"""
Momentum strategy implementation for Tinkoff Invest trading bot
"""
import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy

class MomentumStrategy(BaseStrategy):
    """
    Simple momentum strategy that generates buy/sell signals based on 
    recent price momentum.
    """
    
    def __init__(self, params=None):
        super().__init__(params)
        self.lookback_period = self.params.get('lookback_period', 14)
        self.buy_threshold = self.params.get('buy_threshold', 0.005)
        self.sell_threshold = self.params.get('sell_threshold', 0.005)
    
    def generate_signal(self, data):
        """
        Generate trading signal based on momentum
        
        Args:
            data (pd.DataFrame): DataFrame with OHLCV data
            
        Returns:
            int: 1 for buy, -1 for sell, 0 for no action
        """
        if len(data) < self.lookback_period:
            return 0
            
        # Calculate returns
        if 'returns' not in data.columns:
            data['returns'] = data['close'].pct_change()
            
        # Calculate momentum (sum of returns over lookback period)
        momentum = data['returns'].iloc[-self.lookback_period:].sum()
        
        if momentum > self.buy_threshold:
            return 1
        elif momentum < -self.sell_threshold:
            return -1
        else:
            return 0
