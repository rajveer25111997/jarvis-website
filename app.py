import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# 1. सुपर-फ़ास्ट 3 सेकंड रिफ्रेश
st.set_page_config(page_title="Jarvis 3s Ultra", layout="wide")
st_autorefresh(interval=3000, key="jarvis_ultra_refresh") # 3000ms = 3 Seconds

st.title("🤖 JARVIS : Ultra-Fast 3s Terminal")

# --- फ़ास्ट डेटा हंटर ---
@st.cache_data(ttl=2) # 2 सेकंड की मेमोरी ताकि चार्ट ब्लिंक न करे
def get_ultra_fast_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if df.empty or len(df) < 3:
            df = yf.download(ticker, period="5d", interval="60m", progress=False)
        
        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = df.columns.get_level_values(0)
            
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        return df
    except: return None

# --- सिग्नल लॉजिक ---
def get_signal_box(df, name):
    if df is not None and len(df) > 1:
        e9, e21 = df['EMA9'].iloc[-1], df['EMA21'].iloc[-1]
        if e9 > e21:
            st.success(f"🚀 {name}: BULLISH")
        else:
            st.error(f"📉 {name}: BEARISH")

col1, col2 = st.columns(2)

# --- 🇮🇳 इंडियन मार्केट ---
with col1:
    st.subheader("🇮🇳 NSE Live (3s)")
    in_t = st.text_input("Symbol:", "^NSEI", key="in_key")
    data_in = get_ultra_fast_data(in_t)
    if data_in is not None:
        get_signal_box(data_in, "Jarvis")
        fig = go.Figure(data=[go.Candlestick(x=data_in.index, open=data_in['Open'], 
                        high=data_in['High'], low=data_in['Low'], close=data_in['Close'])])
        fig.add_trace(go.Scatter(x=data_in.index, y=data_in['EMA9'], name="9 EMA", line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=data_in.index, y=data_in['EMA21'], name="21 EMA", line=dict(color='blue')))
        fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Price", f"₹{data_in['Close'].iloc[-1]:,.2f}")

# --- ₿ क्रिप्टो मार्केट ---
with col2:
    st.subheader("₿ Crypto Live (3s)")
    cr_t = st.text_input("Symbol:", "BTC-USD", key="cr_key")
    data_cr = get_ultra_fast_data(cr_t)
    if data_cr is not None:
        get_signal_box(data_cr, "Jarvis")
        fig_c = go.Figure(data=[go.Candlestick(x=data_cr.index, open=data_cr['Open'], 
                          high=data_cr['High'], low=data_cr['Low'], close=data_cr['Close'])])
        fig_c.add_trace(go.Scatter(x=data_cr.index, y=data_cr['EMA9'], name="9 EMA", line=dict(color='orange')))
        fig_c.add_trace(go.Scatter(x=data_cr.index, y=data_cr['EMA21'], name="21 EMA", line=dict(color='blue')))
        fig_c.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_c, use_container_width=True)
        st.metric("Price", f"${data_cr['Close'].iloc[-1]:,.2f}")

st.sidebar.warning("⚡ Ultra-Fast Mode: 3s Refresh")
