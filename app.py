import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# 1. पेज कॉन्फ़िगरेशन और 10 सेकंड का ऑटो-रिफ्रेश
st.set_page_config(page_title="Jarvis 10s Terminal", layout="wide")
st_autorefresh(interval=10000, key="jarvis_fast_refresh") # 10000ms = 10 Seconds

st.title("🤖 JARVIS : Ultra-Fast Dual Monitor (10s Update)")

# --- स्मार्ट डेटा फंक्शन ---
def get_market_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return None

# --- स्क्रीन का बंटवारा (50/50 Split) ---
col1, col2 = st.columns(2)

# --- 🇮🇳 इंडियन मार्केट सेक्शन ---
with col1:
    st.subheader("🇮🇳 Indian Market Live")
    ind_ticker = st.selectbox("इंडेक्स/स्टॉक:", ["^NSEI", "^NSEBANK", "RELIANCE.NS", "SBIN.NS"], index=0)
    ind_data = get_market_data(ind_ticker)
    
    if ind_data is not None and not ind_data.empty:
        # कैंडलस्टिक चार्ट
        fig = go.Figure(data=[go.Candlestick(x=ind_data.index, open=ind_data['Open'], 
                        high=ind_data['High'], low=ind_data['Low'], close=ind_data['Close'])])
        fig.update_layout(template="plotly_dark", height=350, margin=dict(l=0,r=0,b=0,t=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # लाइव भाव
        curr_p = ind_data['Close'].iloc[-1]
        prev_p = ind_data['Open'].iloc[0]
        change = ((curr_p - prev_p) / prev_p) * 100
        st.metric(f"{ind_ticker} Live", f"₹{curr_p:,.2f}", f"{change:.2f}%")

    st.markdown("---")
    st.write("📋 **Nifty 50 Market Movers**")
    ind_watchlist = ["TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "AXISBANK.NS", "TATAMOTORS.NS"]
    grid_in = st.columns(3)
    for i, s in enumerate(ind_watchlist):
        s_df = get_market_data(s)
        if s_df is not None:
            p = s_df['Close'].iloc[-1]
            c = ((p - s_df['Open'].iloc[0]) / s_df['Open'].iloc[0]) * 100
            grid_in[i % 3].metric(s.split('.')[0], f"₹{p:,.1f}", f"{c:.2f}%")

# --- ₿ क्रिप्टो मार्केट सेक्शन ---
with col2:
    st.subheader("₿ Crypto Market 24/7")
    cry_ticker = st.text_input("क्रिप्टो सिंबल:", "BTC-USD")
    cry_data = get_market_data(cry_ticker)
    
    if cry_data is not None and not cry_data.empty:
        fig_c = go.Figure(data=[go.Candlestick(x=cry_data.index, open=cry_data['Open'], 
                         high=cry_data['High'], low=cry_data['Low'], close=cry_data['Close'])])
        fig_c.update_layout(template="plotly_dark", height=350, margin=dict(l=0,r=0,b=0,t=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig_c, use_container_width=True)
        
        # लाइव भाव
        curr_c = cry_data['Close'].iloc[-1]
        prev_c = cry_data['Open'].iloc[0]
        ch_c = ((curr_c - prev_c) / prev_c) * 100
        st.metric(f"{cry_ticker} Live", f"${curr_c:,.2f}", f"{ch_c:.2f}%")

    st.markdown("---")
    st.write("🚀 **Top Crypto Assets**")
    cry_watchlist = ["ETH-USD", "BNB-USD", "SOL-USD", "DOGE-USD", "XRP-USD", "ADA-USD"]
    grid_cr = st.columns(3)
    for i, c in enumerate(cry_watchlist):
        c_df = get_market_data(c)
        if c_df is not None:
            p = c_df['Close'].iloc[-1]
            ch = ((p - c_df['Open'].iloc[0]) / c_df['Open'].iloc[0]) * 100
            grid_cr[i % 3].metric(c.split('-')[0], f"${p:,.2f}", f"{ch:.2f}%")

st.sidebar.write("⏱️ **Jarvis Status:** Running (10s Refresh)")
