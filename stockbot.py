import yfinance as yf
import pandas as pd
import requests
import ta

TOKEN = "8719143523:AAEfud5TmcTbVlSpwqCH7AcloYl9B_I9M0M"
CHAT_ID = "699079139"



sectors = {
    "IT": ["TCS.NS","INFY.NS","WIPRO.NS","HCLTECH.NS","TECHM.NS"],
    "Banking": ["HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","AXISBANK.NS","KOTAKBANK.NS"],
    "Auto": ["MARUTI.NS","TATAMOTORS.NS","M&M.NS","EICHERMOT.NS","BAJAJ-AUTO.NS"],
    "FMCG": ["ITC.NS","HINDUNILVR.NS","NESTLEIND.NS","BRITANNIA.NS","DABUR.NS"],
    "Pharma": ["SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS","DIVISLAB.NS","LUPIN.NS"],
    "Energy": ["RELIANCE.NS","ONGC.NS","IOC.NS","NTPC.NS","POWERGRID.NS"]
}

def get_score(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1d", auto_adjust=True)

        if df.empty or len(df) < 200:
            return None

        close = df["Close"].squeeze()
        volume = df["Volume"].squeeze()

        ma50 = close.rolling(50).mean()
        ma200 = close.rolling(200).mean()

        rsi = ta.momentum.RSIIndicator(close).rsi()
        momentum_1m = close.pct_change(21)

        vol_avg = volume.rolling(20).mean()

        score = 0

        # Trend
        if close.iloc[-1] > ma50.iloc[-1]:
            score += 2
        if close.iloc[-1] > ma200.iloc[-1]:
            score += 2

        # RSI Strength
        if 50 < rsi.iloc[-1] < 70:
            score += 2

        # Momentum
        if momentum_1m.iloc[-1] > 0:
            score += 2

        # Volume confirmation
        if volume.iloc[-1] > vol_avg.iloc[-1]:
            score += 2

        return score

    except:
        return None

message = "📊 STOCK AI REPORT\n"
message += "Updated Every 6 Hours\n"
message += "---------------------------\n"
nifty = yf.download("^NSEI", period="6mo", interval="1d", auto_adjust=True)
nifty_close = nifty["Close"].squeeze()
nifty_ma200 = nifty_close.rolling(200).mean()

if nifty_close.iloc[-1] > nifty_ma200.iloc[-1]:
    market_status = "🟢 Market Trend: BULLISH"
else:
    market_status = "🔴 Market Trend: BEARISH"

message += market_status + "\n"
message += "===========================\n"
for sector, stocks in sectors.items():
    scores = {}

    for s in stocks:
        sc = get_score(s)
        if sc is not None:
            scores[s] = sc

    if not scores:
        continue

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    message += f"\n📌 {sector}\n"
    message += "Bullish 🔥\n"
    for r in ranked[:5]:
        message += f"{r[0]} (Score: {r[1]}/10)\n"

    message += "Bearish ❄️\n"
    for r in ranked[-5:]:
        message += f"{r[0]} (Score: {r[1]}/10)\n"

    message += "---------------------------\n"

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": message
}

requests.post(url, data=payload)
