import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import base64

# 1. सेटअप और 10 सेकंड रिफ्रेश
st.set_page_config(page_title="Jarvis AI: Voice & Scanner", layout="wide")
st_autorefresh(interval=10000, key="jarvis_master_refresh")

# --- वॉइस फंक्शन (पॉइंट 4) ---
def speak_text(text):
    # यह फंक्शन ब्राउज़र में आवाज़ पैदा करेगा
    b64 = base64.b64encode(text.encode()).decode()
    md = f"""
        <iframe src="https://translate.google.com/translate_tts?ie=UTF-8&q={text}&tl=hi&client=tw-ob" allow="autoplay" style="display:none"></iframe>
        """
    st.markdown(md, unsafe_allow_html=True)

# --- डेटा और स्कैनिंग फंक्शन (पॉइंट 3) ---
@st.cache_data(ttl=9)
def get_jarvis_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        return df
    except: return None

st.title("🤖 JARVIS : Voice Alerts & Profit Finder")

col1, col2 = st.columns(2)

# --- 🇮🇳 इंडियन मार्केट + स्कैनर ---
with col1:
    st.header("🇮🇳 Indian Market")
    ind_ticker = st.text_input("Stock:", "^NSEI")
    data_in = get_jarvis_data(ind_ticker)
    
    if data_in is not None:
        # EMA क्रॉसओवर चेक और वॉइस अलर्ट
        e9, e21 = data_in['EMA9'].iloc[-1], data_in['EMA21'].iloc[-1]
        if e9 > e21 and data_in['EMA9'].iloc[-2] <= data_in['EMA21'].iloc[-2]:
            st.warning("🎯 BUY SIGNAL GENERATED!")
            speak_text("राजवीर सर, इंडिया मार्केट में खरीदारी का मौका है")
            
        st.plotly_chart(go.Figure(data=[go.Candlestick(x=data_in.index, open=data_in['Open'], high=data_in['High'], low=data_in['Low'], close=data_in['Close'])]), use_container_width=True)

# --- ₿ क्रिप्टो मार्केट + स्कैनर ---
with col2:
    st.header("₿ Crypto Market")
    cry_ticker = st.text_input("Crypto:", "BTC-USD")
    data_cr = get_jarvis_data(cry_ticker)
    
    if data_cr is not None:
        # EMA क्रॉसओवर चेक और वॉइस अलर्ट
        ce9, ce21 = data_cr['EMA9'].iloc[-1], data_cr['EMA21'].iloc[-1]
        if ce9 > ce21 and data_cr['EMA9'].iloc[-2] <= data_cr['EMA21'].iloc[-2]:
            st.success("🚀 CRYPTO BUY SIGNAL!")
            speak_text("सर, क्रिप्टो में प्रॉफिट का मौका बन रहा है")
            
        st.plotly_chart(go.Figure(data=[go.Candlestick(x=data_cr.index, open=data_cr['Open'], high=data_cr['High'], low=data_cr['Low'], close=data_cr['Close'])]), use_container_width=True)

# --- 🚀 PROFIT FINDER BOXES (नीचे की लिस्ट) ---
st.divider()
st.subheader("🔎 Jarvis Profit Finder (Gainer Scanner)")
s_col1, s_col2, s_col3, s_col4 = st.columns(4)
scan_list = ["TATAMOTORS.NS", "SBIN.NS", "ETH-USD", "SOL-USD"]
scan_cols = [s_col1, s_col2, s_col3, s_col4]

for i, t in enumerate(scan_list):
    df_s = get_jarvis_data(t)
    if df_s is not None:
        change = ((df_s['Close'].iloc[-1] - df_s['Open'].iloc[0]) / df_s['Open'].iloc[0]) * 100
        with scan_cols[i]:
            if abs(change) >= 2.0: # अगर 2% से ज्यादा हलचल है
                st.balloons() # स्क्रीन पर गुब्बारे छोड़ें
                st.error(f"🔥 ALERT: {t} moved {change:.2f}%")
            st.metric(t, f"{df_s['Close'].iloc[-1]:.2f}", f"{change:.2f}%")
