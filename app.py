import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Jarvis Pro: Candle Mode", layout="wide")

# ऑटो रिफ्रेश (हर 30 सेकंड में)
st_autorefresh(interval=30000, key="jarvis_refresh")

st.title("🤖 JARVIS : Professional Candlestick Terminal")

coin = st.sidebar.text_input("कॉइन का नाम (जैसे BTC-USD):", "BTC-USD")

def fetch_candle_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="5m") # 5-min candles for better view
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # आपकी 9/21 EMA स्ट्रेटजी
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        return df
    except:
        return None

data = fetch_candle_data(coin)

if data is not None:
    # --- प्रोफेशनल कैंडलस्टिक चार्ट (Plotly) ---
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                    open=data['Open'], high=data['High'],
                    low=data['Low'], close=data['Close'], name='Price'),
                    go.Scatter(x=data.index, y=data['EMA9'], line=dict(color='orange', width=1), name='EMA 9'),
                    go.Scatter(x=data.index, y=data['EMA21'], line=dict(color='blue', width=1), name='EMA 21')])

    # ज़ूम और लुक सेटिंग
    fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark", 
                      height=600, title=f"Live {coin} 5-Minute Candles")
    
    st.plotly_chart(fig, use_container_width=True)

    # जार्विस का लाइव फैसला
    last_p = float(data['Close'].iloc[-1])
    st.metric("LIVE PRICE", f"${last_p:,.2f}")
    
    if data['EMA9'].iloc[-1] > data['EMA21'].iloc[-1]:
        st.success("🎯 जार्विस सिग्नल: BULLISH (Buy Entry Possible)")
    else:
        st.error("📉 जार्विस सिग्नल: BEARISH (Wait for Recovery)")
else:
    st.warning("डेटा लोड हो रहा है...")
