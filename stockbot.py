import yfinance as yf
import pandas as pd
import requests
import ta

TOKEN = "8719143523:AAEfud5TmcTbVlSpwqCH7AcloYl9B_I9M0M"
CHAT_ID = "699079139"


# -------------------- STOCKS BY SECTOR --------------------
sectors = {
    "IT": ["TCS.NS","INFY.NS","WIPRO.NS","HCLTECH.NS","TECHM.NS"],
    "Banking": ["HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","AXISBANK.NS","KOTAKBANK.NS"],
    "Auto": ["MARUTI.NS","TATAMOTORS.NS","M&M.NS","EICHERMOT.NS","BAJAJ-AUTO.NS"],
    "FMCG": ["ITC.NS","HINDUNILVR.NS","NESTLEIND.NS","BRITANNIA.NS","DABUR.NS"],
    "Pharma": ["SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS","DIVISLAB.NS","LUPIN.NS"],
    "Energy": ["RELIANCE.NS","ONGC.NS","IOC.NS","NTPC.NS","POWERGRID.NS"]
}

# -------------------- STOCK SCORING FUNCTION --------------------
def get_score(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1d", auto_adjust=True, progress=False)
        if df.empty or len(df) < 50:
            print(f"{ticker}: Not enough data")
            return None

        # Ensure close and volume are 1D Series
        close = df["Close"].iloc[:,0] if isinstance(df["Close"], pd.DataFrame) else df["Close"]
        volume = df["Volume"].iloc[:,0] if isinstance(df["Volume"], pd.DataFrame) else df["Volume"]

        ma50 = close.rolling(50).mean()
        ma200 = close.rolling(200).mean()

        rsi = ta.momentum.RSIIndicator(close).rsi().dropna()
        momentum_1m = close.pct_change(21)
        vol_avg = volume.rolling(20).mean()

        score = 0
        if not ma50.empty and close.iloc[-1] > ma50.iloc[-1]:
            score += 2
        if not ma200.empty and close.iloc[-1] > ma200.iloc[-1]:
            score += 2
        if not rsi.empty and 50 < rsi.iloc[-1] < 70:
            score += 2
        if not momentum_1m.empty and momentum_1m.iloc[-1] > 0:
            score += 2
        if not vol_avg.empty and volume.iloc[-1] > vol_avg.iloc[-1]:
            score += 2

        print(f"{ticker}: Score = {score}/10")
        return score

    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

# -------------------- BUILD TELEGRAM MESSAGE --------------------
message = "📊 STOCK AI REPORT\n"
message += "Updated Every 6 Hours\n"
message += "---------------------------\n"

for sector_name, stocks in sectors.items():
    scores = {}

    for ticker in stocks:
        sc = get_score(ticker)
        if sc is not None:
            scores[ticker] = sc

    if not scores:
        print(f"No valid scores for {sector_name}")
        continue

    # Sort stocks by score descending
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    message += f"\n📌 {sector_name}\n"

    # Top 3 bullish
    message += "Bullish 🔥\n"
    for r in ranked[:3]:
        message += f"{r[0]} (Score: {r[1]}/10)\n"

    # Top 3 bearish
    message += "Bearish ❄️\n"
    for r in ranked[-3:]:
        message += f"{r[0]} (Score: {r[1]}/10)\n"

    message += "---------------------------\n"

# -------------------- SEND TO TELEGRAM --------------------
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": message
}

response = requests.post(url, json=payload)
if response.status_code == 200:
    print("Message sent successfully ✅")
else:
    print(f"Failed to send message ❌: {response.text}")
