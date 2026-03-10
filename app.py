import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# --- JARVIS SETTINGS (Yahan aap apne niyam set kar sakte hain) ---
RULES = {
    "RISK_REWARD": 1.0,        # 1:1 Ratio
    "STOP_LOSS_POINTS": 50,    # Nifty points mein SL
    "TARGET_POINTS": 50,      # Nifty points mein Target
    "EMA_SHORT": 9,
    "EMA_LONG": 21,
    "RSI_THRESHOLD": 50
}

st.set_page_config(page_title="Jarvis Option Backtester", layout="wide")
st.title("🤖 Jarvis Point-Based Option Backtester")

symbol = st.sidebar.text_input("Ticker (e.g., ^NSEI)", "^NSEI")
year_to_test = st.sidebar.selectbox("Test Duration", ["1y", "2y", "5y"])

# 1. Data Fetching
@st.cache_data
def get_historical_data(ticker, prd):
    data = yf.download(ticker, period=prd, interval="1h")
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data

df = get_historical_data(symbol, year_to_test)

if not df.empty:
    # 2. Indicators (Jarvis Brain)
    df['EMA9'] = ta.ema(df['Close'], length=RULES["EMA_SHORT"])
    df['EMA21'] = ta.ema(df['Close'], length=RULES["EMA_LONG"])
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    # SMC Logic: Fair Value Gap
    df['FVG'] = (df['Low'].shift(-2) > df['High']) & (df['Close'].shift(-1) > df['High'])

    # 3. Backtesting Logic (Point Based)
    trades = []
    in_trade = False
    
    for i in range(50, len(df)-5):
        # Aapke Niyam:
        entry_condition = (
            df['EMA9'].iloc[i] > df['EMA21'].iloc[i] and 
            df['RSI'].iloc[i] > RULES["RSI_THRESHOLD"] and
            df['FVG'].iloc[i-1]
        )

        if entry_condition and not in_trade:
            entry_price = float(df['Close'].iloc[i])
            sl_price = entry_price - RULES["STOP_LOSS_POINTS"]
            tp_price = entry_price + RULES["TARGET_POINTS"]
            in_trade = True
            
            # Point Calculation
            for j in range(i+1, len(df)):
                curr_high = float(df['High'].iloc[j])
                curr_low = float(df['Low'].iloc[j])
                
                if curr_low <= sl_price:
                    trades.append({'Date': df.index[j], 'Type': 'BUY', 'Points': -RULES["STOP_LOSS_POINTS"], 'Status': 'SL HIT'})
                    in_trade = False
                    break
                elif curr_high >= tp_price:
                    trades.append({'Date': df.index[j], 'Type': 'BUY', 'Points': RULES["TARGET_POINTS"], 'Status': 'TARGET HIT'})
                    in_trade = False
                    break

    # 4. Result Dashboard
    if trades:
        res = pd.DataFrame(trades)
        total_points = res['Points'].sum()
        win_rate = (res['Status'] == 'TARGET HIT').mean() * 100
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Points Earned", f"{total_points} pts")
        c2.metric("Win Rate", f"{win_rate:.2f}%")
        c3.metric("Total Trades", len(res))
        
        st.subheader("📊 Trade Log (Jarvis Analysis)")
        st.dataframe(res)
    else:
        st.warning("Jarvis ko koi trade nahi mila. Niyam thode badal kar dekhein.")

