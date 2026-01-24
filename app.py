import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import base64

st.set_page_config(page_title="Jarvis Smart Hybrid", layout="wide")
st_autorefresh(interval=10000, key="jarvis_hybrid_refresh")

# --- वॉइस अलर्ट ---
def speak_text(text):
    b64 = base64.b64encode(text.encode()).decode()
    md = f"""<iframe src="https://translate.google.com/translate_tts?ie=UTF-8&q={text}&tl=hi&client=tw-ob" allow="autoplay" style="display:none"></iframe>"""
    st.markdown(md, unsafe_allow_html=True)

# --- स्मार्ट डेटा हंटर (Live + Historical) ---
@st.cache_data(ttl=9)
def get_smart_data(ticker):
    try:
        # पहले लाइव डेटा (1m) कोशिश करें
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        
        # अगर 1 मिनट वाला डेटा नहीं मिला (मार्केट बंद है), तो पिछले 5 दिन का डेटा लाएं
        if df.empty or len(df) < 5:
            df = yf.download(ticker, period="5d", interval="60m", progress=False)
            st.sidebar.info(f"ℹ️ {ticker}: मार्केट बंद है, पिछला डेटा दिखा रहा हूँ।")
        else:
            st.sidebar.success(f"🟢 {ticker}: लाइव मार्केट चालू है।")

        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = df.columns.get_level_values(0)
            
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        return df
    except: return None

st.title("🤖 JARVIS : Smart Market Intelligence")

col1, col2 = st.columns(2)

# --- 🇮🇳 इंडियन मार्केट (NSE) ---
with col1:
    st.header("🇮🇳 Indian Market")
    ind_ticker = st.text_input("Stock:", "^NSEI")
    data_in = get_smart_data(ind_ticker)
    
    if data_in is not None:
        fig = go.Figure(data=[go.Candlestick(x=data_in.index, open=data_in['Open'], high=data_in['High'], low=data_in['Low'], close=data_in['Close'])])
        fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, title=f"{ind_ticker} Analysis")
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Price", f"₹{data_in['Close'].iloc[-1]:,.2f}")

# --- ₿ क्रिप्टो मार्केट (24/7) ---
with col2:
    st.header("₿ Crypto Market")
    cry_ticker = st.text_input("Crypto:", "BTC-USD")
    data_cr = get_smart_data(cry_ticker)
    
    if data_cr is not None:
        fig_c = go.Figure(data=[go.Candlestick(x=data_cr.index, open=data_cr['Open'], high=data_cr['High'], low=data_cr['Low'], close=data_cr['Close'])])
        fig_c.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, title=f"{cry_ticker} Analysis")
        st.plotly_chart(fig_c, use_container_width=True)
        st.metric("Price", f"${data_cr['Close'].iloc[-1]:,.2f}")

# --- 🔎 वॉचलिस्ट ---
st.divider()
st.subheader("📋 Live Watchlist & Gainers")
w_list = ["TCS.NS", "RELIANCE.NS", "ETH-USD", "DOGE-USD"]
w_cols = st.columns(4)

for i, t in enumerate(w_list):
    d = get_smart_data(t)
    if d is not None:
        p = d['Close'].iloc[-1]
        ch = ((p - d['Open'].iloc[0]) / d['Open'].iloc[0]) * 100
        w_cols[i].metric(t, f"{p:,.1f}", f"{ch:.2f}%")
