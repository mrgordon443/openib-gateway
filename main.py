import requests
import pandas as pd
import os

# === Load credentials from GitHub Secrets ===
import os

OANDA_API_KEY = os.environ["OANDA_API_KEY"]
OANDA_ACCOUNT_ID = os.environ["OANDA_ACCOUNT_ID"]

# === Constants ===
OANDA_URL = "https://api-fxpractice.oanda.com/v3"
HEADERS = {
    "Authorization": f"Bearer {OANDA_API_KEY}",
    "Content-Type": "application/json"
}
INSTRUMENT = "EUR_USD"
UNITS = "100"  # Positive = Buy, Negative = Sell

# === Get historical candles ===
def get_candles(instrument, count=100, granularity="M5"):
    url = f"{OANDA_URL}/instruments/{instrument}/candles"
    params = {
        "count": count,
        "granularity": granularity,
        "price": "M"
    }
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    candles = response.json()["candles"]
    data = pd.DataFrame([{
        "time": c["time"],
        "close": float(c["mid"]["c"])
    } for c in candles])
    return data

# === RSI Calculation ===
def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# === Place market order ===
def place_order(units):
    url = f"{OANDA_URL}/accounts/{OANDA_ACCOUNT_ID}/orders"
    data = {
        "order": {
            "instrument": INSTRUMENT,
            "units": units,
            "type": "MARKET",
            "positionFill": "DEFAULT"
        }
    }
    response = requests.post(url, headers=HEADERS, json=data)
    if response.status_code == 201:
        print(f"✅ Order placed: {units} units of {INSTRUMENT}")
    else:
        print("❌ Order failed")
        print(response.text)

# === Run Bot ===
def run_bot():
    df = get_candles(INSTRUMENT)
    df["RSI"] = calculate_rsi(df["close"])

    latest_rsi = df["RSI"].iloc[-1]
    print(f"Latest RSI: {latest_rsi:.2f}")

    if latest_rsi < 30:
        print("RSI indicates oversold - placing BUY order")
        place_order(UNITS)
    elif latest_rsi > 70:
        print("RSI indicates overbought - placing SELL order")
        place_order(f"-{UNITS}")
    else:
        print("RSI neutral - no action")

if __name__ == "__main__":
    run_bot()

