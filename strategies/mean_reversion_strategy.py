"""
Mean Reversion strategy implementation for Tinkoff Invest trading bot
"""
import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy

class MeanReversionStrategy(BaseStrategy):
    """
    Mean reversion strategy that generates buy/sell signals based on 
    price deviations from a moving average.
    """
    
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get('window', 20)
        self.std_dev_threshold = self.params.get('std_dev_threshold', 1.5)
    
    def generate_signal(self, data):
        """
        Generate trading signal based on mean reversion
        
        Args:
            data (pd.DataFrame): DataFrame with OHLCV data
            
        Returns:
            int: 1 for buy, -1 for sell, 0 for no action
        """
        if len(data) < self.window:
            return 0
            
        # Calculate moving average and standard deviation
        data['ma'] = data['close'].rolling(window=self.window).mean()
        data['std'] = data['close'].rolling(window=self.window).std()
        
        # Calculate z-score (how many standard deviations away from mean)
        data['z_score'] = (data['close'] - data['ma']) / data['std']
        
        # Get the most recent z-score
        current_z = data['z_score'].iloc[-1]
        
        # Generate signals based on z-score
        if current_z < -self.std_dev_threshold:
            # Price is significantly below average, expect reversion upward -> BUY
            return 1
        elif current_z > self.std_dev_threshold:
            # Price is significantly above average, expect reversion downward -> SELL
            return -1
        else:
            # Price is within normal range, no signal
            return 0
