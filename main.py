import requests
import json
import pandas as pd
from datetime import datetime
import time

class OANDATrader:
    def __init__(self, api_key, account_id, environment='practice'):
        self.api_key = api_key
        self.account_id = account_id
        
        # Set up the base URL based on environment
        if environment == 'practice':
            self.base_url = 'https://api-fxpractice.oanda.com'
        else:
            self.base_url = 'https://api-fxtrade.oanda.com'
            
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_account_info(self):
        """Get account information"""
        url = f"{self.base_url}/v3/accounts/{self.account_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def get_instruments(self):
        """Get available trading instruments"""
        url = f"{self.base_url}/v3/accounts/{self.account_id}/instruments"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def get_prices(self, instruments):
        """Get current prices for instruments"""
        instruments_str = ','.join(instruments)
        url = f"{self.base_url}/v3/accounts/{self.account_id}/pricing"
        params = {'instruments': instruments_str}
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()
    
    def get_candles(self, instrument, count=100, granularity='M5'):
        """Get historical candle data"""
        url = f"{self.base_url}/v3/instruments/{instrument}/candles"
        params = {
            'count': count,
            'granularity': granularity,
            'price': 'MBA'  # Mid, Bid, Ask prices
        }
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()
    
    def create_market_order(self, instrument, units, stop_loss=None, take_profit=None):
        """Create a market order"""
        url = f"{self.base_url}/v3/accounts/{self.account_id}/orders"
        
        order_data = {
            "order": {
                "type": "MARKET",
                "instrument": instrument,
                "units": str(units),
                "timeInForce": "FOK",
                "positionFill": "DEFAULT"
            }
        }
        
        # Add stop loss if provided
        if stop_loss:
            order_data["order"]["stopLossOnFill"] = {
                "price": str(stop_loss)
            }
        
        # Add take profit if provided
        if take_profit:
            order_data["order"]["takeProfitOnFill"] = {
                "price": str(take_profit)
            }
        
        response = requests.post(url, headers=self.headers, json=order_data)
        return response.json()
    
    def create_limit_order(self, instrument, units, price, stop_loss=None, take_profit=None):
        """Create a limit order"""
        url = f"{self.base_url}/v3/accounts/{self.account_id}/orders"
        
        order_data = {
            "order": {
                "type": "LIMIT",
                "instrument": instrument,
                "units": str(units),
                "price": str(price),
                "timeInForce": "GTC"
            }
        }
        
        # Add stop loss if provided
        if stop_loss:
            order_data["order"]["stopLossOnFill"] = {
                "price": str(stop_loss)
            }
        
        # Add take profit if provided
        if take_profit:
            order_data["order"]["takeProfitOnFill"] = {
                "price": str(take_profit)
            }
        
        response = requests.post(url, headers=self.headers, json=order_data)
        return response.json()
    
    def get_open_positions(self):
        """Get all open positions"""
        url = f"{self.base_url}/v3/accounts/{self.account_id}/openPositions"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def close_position(self, instrument, units="ALL"):
        """Close a position"""
        url = f"{self.base_url}/v3/accounts/{self.account_id}/positions/{instrument}/close"
        
        # Determine if closing long or short position
        if units == "ALL":
            data = {"longUnits": "ALL", "shortUnits": "ALL"}
        elif units > 0:
            data = {"longUnits": str(units)}
        else:
            data = {"shortUnits": str(abs(units))}
        
        response = requests.put(url, headers=self.headers, json=data)
        return response.json()
    
    def calculate_sma(self, prices, period):
        """Calculate Simple Moving Average"""
        return sum(prices[-period:]) / period if len(prices) >= period else None
    
    def calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return None
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [delta if delta > 0 else 0 for delta in deltas]
        losses = [-delta if delta < 0 else 0 for delta in deltas]
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

def simple_trading_strategy(trader, instrument='EUR_USD'):
    """
    Simple trading strategy using RSI and moving averages
    """
    print(f"Starting trading strategy for {instrument}")
    print(f"RSI Value: {rsi}")
    # Get historical data
    candles_data = trader.get_candles(instrument, count=50, granularity='M5')
    
    if 'candles' not in candles_data:
        print("Error getting candle data")
        return
    
    # Extract closing prices
    closes = []
    for candle in candles_data['candles']:
        if candle['complete']:
            closes.append(float(candle['mid']['c']))
    
    if len(closes) < 20:
        print("Not enough data for analysis")
        return
    
    # Calculate indicators
    sma_20 = trader.calculate_sma(closes, 20)
    sma_50 = trader.calculate_sma(closes, 50)
    rsi = trader.calculate_rsi(closes)
    current_price = closes[-1]
    
    print(f"Current Price: {current_price}")
    print(f"SMA 20: {sma_20}")
    print(f"SMA 50: {sma_50}")
    print(f"RSI: {rsi}")
    
    # Trading logic
    if rsi and sma_20 and sma_50:
        # Buy signal: RSI oversold and short SMA above long SMA
        if rsi < 30 and sma_20 > sma_50:
    print("BUY signal: RSI is low (<30) and short-term SMA is above long-term SMA")
    # Place buy order here

elif rsi > 70 and sma_20 < sma_50:
    print("SELL signal: RSI is high (>70) and short-term SMA is below long-term SMA")
    # Place sell order here

else:
    print("HOLD: No valid trading signal - RSI not extreme or SMA crossover not met")
            print("BUY SIGNAL DETECTED!")
            # Calculate stop loss and take profit
            stop_loss = current_price * 0.99  # 1% stop loss
            take_profit = current_price * 1.02  # 2% take profit
            
            # Place buy order (1000 units)
            order_result = trader.create_market_order(
                instrument=instrument,
                units=1000,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            print("Order result:", order_result)
        
        # Sell signal: RSI overbought and short SMA below long SMA
        elif rsi > 70 and sma_20 < sma_50:
            print("SELL SIGNAL DETECTED!")
            # Calculate stop loss and take profit
            stop_loss = current_price * 1.01  # 1% stop loss
            take_profit = current_price * 0.98  # 2% take profit
            
            # Place sell order (-1000 units)
            order_result = trader.create_market_order(
                instrument=instrument,
                units=-1000,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            print("Order result:", order_result)
        else:
            print("No trading signal")

def main():
    # IMPORTANT: You need to set these values
    # Get your API key from OANDA's developer portal
    API_KEY = "YOUR_OANDA_API_KEY_HERE"
    ACCOUNT_ID = "YOUR_ACCOUNT_ID_HERE"
    
    if API_KEY == "YOUR_OANDA_API_KEY_HERE":
        print("Please set your OANDA API key and account ID in the code")
        print("1. Go to https://www.oanda.com/demo-account/tpa/personal_token")
        print("2. Create a practice account and get your API token")
        print("3. Replace the API_KEY and ACCOUNT_ID in this script")
        return
    
    # Initialize trader (using practice environment)
    trader = OANDATrader(API_KEY, ACCOUNT_ID, environment='practice')
    
    try:
        # Get account info
        account_info = trader.get_account_info()
        print("Account Info:", json.dumps(account_info, indent=2))
        
        # Get current prices for major pairs
        major_pairs = ['EUR_USD', 'GBP_USD', 'USD_JPY', 'AUD_USD']
        prices = trader.get_prices(major_pairs)
        print("\nCurrent Prices:")
        for price in prices.get('prices', []):
            print(f"{price['instrument']}: Bid={price['bids'][0]['price']}, Ask={price['asks'][0]['price']}")
        
        # Get open positions
        positions = trader.get_open_positions()
        print(f"\nOpen Positions: {len(positions.get('positions', []))}")
        
        # Run trading strategy
        print("\n" + "="*50)
        simple_trading_strategy(trader, 'EUR_USD')
        
        # Example of creating different order types
        print("\n" + "="*50)
        print("Example order operations (commented out for safety):")
        print("# Market buy order:")
        print("# trader.create_market_order('EUR_USD', 1000)")
        print("# Limit sell order:")
        print("# trader.create_limit_order('EUR_USD', -1000, 1.1000)")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
