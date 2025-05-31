import yfinance as yf
import pandas as pd

# Download stock data
data = yf.download("AAPL", start="2023-01-01", end="2024-01-01")

# Calculate RSI
delta = data['Close'].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)

avg_gain = gain.rolling(window=14).mean()
avg_loss = loss.rolling(window=14).mean()

rs = avg_gain / avg_loss
rsi = 100 - (100 / (1 + rs))
data['RSI'] = rsi

# Create signals
data['Signal'] = 'Hold'
data.loc[data['RSI'] < 30, 'Signal'] = 'Buy'
data.loc[data['RSI'] > 70, 'Signal'] = 'Sell'

# Show signals
signals = data[data['Signal'] != 'Hold'][['Close', 'RSI', 'Signal']]
print("Trading Signals Based on RSI:\n")
print(signals)
