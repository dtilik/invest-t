"""
Base strategy module for Tinkoff Invest trading bot
"""

class BaseStrategy:
    """Base class for all trading strategies"""
    
    def __init__(self, params=None):
        self.params = params or {}
    
    def generate_signal(self, data):
        """
        Generate trading signal based on data
        Returns: 
            1 for buy signal
            -1 for sell signal
            0 for no action
        """
        raise NotImplementedError("Subclasses must implement this method")
