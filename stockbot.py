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
    df = yf.download(ticker, period="3mo", interval="1d")
    if len(df) < 50:
        return None
    df["rsi"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
    df["ma50"] = df["Close"].rolling(50).mean()
    last = df.iloc[-1]
    score = 0
    if last["Close"] > last["ma50"]:
        score += 1
    if last["rsi"] < 70:
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
