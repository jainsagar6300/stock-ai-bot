import yfinance as yf
import pandas as pd
import requests
import ta

TOKEN = "8719143523:AAEfud5TmcTbVlSpwqCH7AcloYl9B_I9M0M"
CHAT_ID = "699079139"

# -------------------- DEFAULT NSE 100 TICKERS WITH GROUP B SECTORS --------------------
# Only a sample subset shown here; for full coverage, expand with all Nifty 100 tickers
sectors = {
    "Technology": ["TCS.NS","INFY.NS","WIPRO.NS","HCLTECH.NS","TECHM.NS"],
    "Financials": ["HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","AXISBANK.NS","KOTAKBANK.NS","BAJFINANCE.NS","HDFC.NS","ICICIGI.NS"],
    "Consumer": ["ITC.NS","HINDUNILVR.NS","NESTLEIND.NS","BRITANNIA.NS","DABUR.NS","MARICO.NS","TITAN.NS","ULTRACEMCO.NS"],
    "Healthcare": ["SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS","DIVISLAB.NS","LUPIN.NS"],
    "Energy": ["RELIANCE.NS","ONGC.NS","IOC.NS","NTPC.NS","POWERGRID.NS","BPCL.NS","GAIL.NS"],
    "Industrials": ["LT.NS","BHARTIARTL.NS","GRASIM.NS","SIEMENS.NS","ABB.NS"],
    "Materials": ["TATASTEEL.NS","JSWSTEEL.NS","HINDALCO.NS","VEDL.NS","COALINDIA.NS"],
    "Telecom": ["BHARTIARTL.NS","IDEA.NS"]
}

# -------------------- SCORING FUNCTION --------------------
def get_score(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1d", auto_adjust=True, progress=False)
        if df.empty or len(df) < 50:
            print(f"{ticker}: Not enough data")
            return None

        # Ensure 1D Series
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

# -------------------- CALCULATE SCORES AND SECTOR AVERAGES --------------------
sector_scores = {}
sector_stock_scores = {}

for sector_name, tickers in sectors.items():
    scores = {}
    for ticker in tickers:
        sc = get_score(ticker)
        if sc is not None:
            scores[ticker] = sc
    if scores:
        avg_score = sum(scores.values()) / len(scores)
        sector_scores[sector_name] = avg_score
        sector_stock_scores[sector_name] = scores
    else:
        print(f"No valid scores for sector {sector_name}")

# Rank sectors by average score
ranked_sectors = sorted(sector_scores.items(), key=lambda x: x[1], reverse=True)

# -------------------- BUILD TELEGRAM MESSAGE --------------------
message = "📊 NSE 100 STOCK AI REPORT\n"
message += "Updated Every 6 Hours\n"
message += "---------------------------\n"

# Add sector strength ranking
message += "📈 Sector Strength Ranking\n"
for idx, (sector, avg_score) in enumerate(ranked_sectors, start=1):
    message += f"{idx}. {sector} — Avg Score: {avg_score:.2f}\n"
message += "---------------------------\n"

# Add top 3 bullish / bottom 3 bearish per sector
for sector_name, _ in ranked_sectors:
    scores = sector_stock_scores[sector_name]
    ranked_stocks = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    message += f"\n📌 {sector_name}\n"
    message += "Bullish 🔥\n"
    for r in ranked_stocks[:3]:
        message += f"{r[0]} (Score: {r[1]}/10)\n"
    message += "Bearish ❄️\n"
    for r in ranked_stocks[-3:]:
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
