import yfinance as yf
import pandas as pd
from telegram import Bot
import ta

TOKEN = "8719143523:AAEfud5TmcTbVlSpwqCH7AcloYl9B_I9M0M"
CHAT_ID = "699079139"

bot = Bot(TOKEN)

sectors = {
    "IT": ["TCS.NS","INFY.NS","WIPRO.NS","HCLTECH.NS","TECHM.NS"],
    "Banking": ["HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","AXISBANK.NS","KOTAKBANK.NS"],
    "Auto": ["MARUTI.NS","TATAMOTORS.NS","M&M.NS","EICHERMOT.NS","BAJAJ-AUTO.NS"],
    "FMCG": ["ITC.NS","HINDUNILVR.NS","NESTLEIND.NS","BRITANNIA.NS","DABUR.NS"],
    "Pharma": ["SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS","DIVISLAB.NS","LUPIN.NS"],
    "Energy": ["RELIANCE.NS","ONGC.NS","IOC.NS","NTPC.NS","POWERGRID.NS"]
}

def get_score(ticker):
    df = yf.download(ticker, period="3mo", interval="1d", auto_adjust=True)

    if df.empty or len(df) < 50:
        return None

    # Make sure Close is 1D
    close = df["Close"].squeeze()

    # Calculate indicators safely
    rsi = ta.momentum.RSIIndicator(close).rsi()
    ma50 = close.rolling(50).mean()

    last_close = close.iloc[-1]
    last_rsi = rsi.iloc[-1]
    last_ma50 = ma50.iloc[-1]

    score = 0

    if last_close > last_ma50:
        score += 1
    if last_rsi < 70:
        score += 1

    return score

message = "📊 Stock AI Report\n\n"

for sector, stocks in sectors.items():
    scores = {}
    for s in stocks:
        sc = get_score(s)
        if sc is not None:
            scores[s] = sc
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    message += f"\n{sector}\n"
    message += "Bullish:\n"
    for r in ranked[:5]:
        message += r[0] + "\n"
    message += "Bearish:\n"
    for r in ranked[-5:]:
        message += r[0] + "\n"

bot.send_message(chat_id=CHAT_ID, text=message)
