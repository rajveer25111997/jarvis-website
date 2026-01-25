import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import base64

# 1. 'ब्रह्मांड की गति' - 1 सेकंड रिफ्रेश
st.set_page_config(page_title="Jarvis 1s Ultra-Fast", layout="wide")
st_autorefresh(interval=1000, key="jarvis_1s_refresh") # 1000ms = 1 Second

def speak_text(text):
    audio_html = f"""<audio autoplay><source src="https://translate.google.com/translate_tts?ie=UTF-8&q={text}&tl=hi&client=tw-ob" type="audio/mpeg"></audio>"""
    st.markdown(audio_html, unsafe_allow_html=True)

# --- डेटा इंजन (1 सेकंड की लोडिंग के लिए ऑप्टिमाइज्ड) ---
@st.cache_data(ttl=1) # सिर्फ 1 सेकंड की याददाश्त
def get_1s_data(ticker, period="1d", interval="1m"):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return None

st.title("🤖 JARVIS : Extreme 1s Live Terminal")

# --- टॉप बार: न्यूज़ और अलर्ट ---
st.markdown("<marquee style='color: #00FF00; font-weight: bold; background: #1E1E1E; padding: 5px;'>🚀 जार्विस हर 1 सेकंड में बाज़ार को स्कैन कर रहा है... लाइव डेटा फीड एक्टिव है... </marquee>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

# --- 🇮🇳 LIVE NSE (1s Update) ---
with col1:
    st.header("🇮🇳 India Live")
    in_t = st.text_input("Symbol:", "^NSEI")
    data_in = get_1s_data(in_t)
    if data_in is not None:
        price = data_in['Close'].iloc[-1]
        st.metric(f"{in_t} LIVE", f"₹{price:,.2f}")
        
        fig = go.Figure(data=[go.Candlestick(x=data_in.index, open=data_in['Open'], high=data_in['High'], low=data_in['Low'], close=data_in['Close'])])
        fig.update_layout(template="plotly_dark", height=350, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

# --- ₿ LIVE CRYPTO (1s Update) ---
with col2:
    st.header("₿ Crypto Live")
    cr_t = st.text_input("Symbol:", "BTC-USD")
    data_cr = get_1s_data(cr_t)
    if data_cr is not None:
        price_c = data_cr['Close'].iloc[-1]
        st.metric(f"{cr_t} LIVE", f"${price_c:,.2f}")
        
        fig_c = go.Figure(data=[go.Candlestick(x=data_cr.index, open=data_cr['Open'], high=data_cr['High'], low=data_cr['Low'], close=data_cr['Close'])])
        fig_c.update_layout(template="plotly_dark", height=350, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig_c, use_container_width=True)

# --- 🏆 10-YEAR MULTI-BAGGER SCANNER (पॉइंट 12) ---
st.divider()
st.subheader("🏆 10-Year Wealth Creators (Long Term Analysis)")
lt_stocks = ["TCS.NS", "TITAN.NS", "RELIANCE.NS", "ASIANPAINT.NS"]
lt_cols = st.columns(4)

for i, t in enumerate(lt_stocks):
    # 10 साल का डेटा स्कैन
    df_lt = get_1s_data(t, period="10y", interval="1d")
    if df_lt is not None:
        growth = ((df_lt['Close'].iloc[-1] - df_lt['Close'].iloc[0]) / df_lt['Close'].iloc[0]) * 100
        with lt_cols[i]:
            st.write(f"**{t.split('.')[0]}**")
            st.write(f"10Y Growth: {growth:.1f}%")
            if growth > 500: st.success("💎 MULTI-BAGGER")

if st.sidebar.button("जावेद रिपोर्ट दो 🎤"):
    speak_text("राजवीर सर, जार्विस अब हर एक सेकंड में बाज़ार की धड़कन महसूस कर रहा है।")
