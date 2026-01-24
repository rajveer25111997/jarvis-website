import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# 1. सेटअप और 10 सेकंड रिफ्रेश
st.set_page_config(page_title="Jarvis Anti-Flicker", layout="wide")
st_autorefresh(interval=10000, key="jarvis_refresh")

st.title("🤖 JARVIS : Continuous Live Monitor")

# --- डेटा फेचिंग (बिना चार्ट गायब किए) ---
@st.cache_data(ttl=9) # 9 सेकंड तक डेटा को याद रखेगा ताकि चार्ट गायब न हो
def get_fast_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return None

def draw_chart(df, title):
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(template="plotly_dark", height=380, margin=dict(l=0,r=0,b=0,t=0), xaxis_rangeslider_visible=False)
    return fig

# --- मेन डैशबोर्ड ---
col1, col2 = st.columns(2)

# --- इंडियन मार्केट (Left) ---
with col1:
    st.subheader("🇮🇳 NSE Live")
    ind_t = "RELIANCE.NS" if st.sidebar.button("Switch to Reliance") else "^NSEI"
    data_in = get_fast_data(ind_t)
    
    if data_in is not None and not data_in.empty:
        st.plotly_chart(draw_chart(data_in, ind_t), use_container_width=True, config={'displayModeBar': False})
        curr = data_in['Close'].iloc[-1]
        st.metric("Current Price", f"₹{curr:,.2f}")
    
    st.write("📈 **Top Indian Movers**")
    i_list = ["TCS.NS", "SBIN.NS", "HDFCBANK.NS"]
    c1, c2, c3 = st.columns(3)
    for i, s in enumerate(i_list):
        d = get_fast_data(s)
        if d is not None:
            [c1, c2, c3][i].metric(s.split('.')[0], f"₹{d['Close'].iloc[-1]:,.0f}")

# --- क्रिप्टो मार्केट (Right) ---
with col2:
    st.subheader("₿ Crypto Live")
    cry_t = "BTC-USD"
    data_cry = get_fast_data(cry_t)
    
    if data_cry is not None and not data_cry.empty:
        st.plotly_chart(draw_chart(data_cry, cry_t), use_container_width=True, config={'displayModeBar': False})
        curr_c = data_cry['Close'].iloc[-1]
        st.metric("Current Price", f"${curr_c:,.2f}")

    st.write("🚀 **Top Crypto Movers**")
    c_list = ["ETH-USD", "SOL-USD", "DOGE-USD"]
    cc1, cc2, cc3 = st.columns(3)
    for i, s in enumerate(c_list):
        d = get_fast_data(s)
        if d is not None:
            [cc1, cc2, cc3][i].metric(s.split('-')[0], f"${d['Close'].iloc[-1]:,.1f}")

st.sidebar.success("✅ Jarvis is Tracking Live")
