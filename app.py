import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. NSE CONFIG ---
st.set_page_config(page_title="JARVIS-R: NSE SNIPER", layout="wide")
st_autorefresh(interval=5000, key="nse_fix_refresh")

# --- 🧠 2. NSE DATA ENGINE (Fixed Error Handling) ---
def get_nse_data(symbol):
    try:
        # '1d' period and '1m' interval may fail on weekends
        df = yf.download(symbol, period="5d", interval="1m", progress=False, auto_adjust=True)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): 
                df.columns = df.columns.get_level_values(0)
            # सिर्फ आज का या सबसे लेटेस्ट डेटा लें
            return df.tail(100) 
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

# --- 🔊 3. VOICE ENGINE ---
def jarvis_speak(text):
    js = f"<script>var m=new SpeechSynthesisUtterance('{text}');window.speechSynthesis.speak(m);</script>"
    st.components.v1.html(js, height=0)

# --- 🏦 4. UI BRANDING ---
st.markdown("""
    <div style='text-align:center; background:linear-gradient(90deg, #1e3c72, #2a5298); padding:15px; border-radius:15px; border:2px solid #fff;'>
        <h1 style='color:white; margin:0;'>🤖 JARVIS-R: NSE/BSE SNIPER</h1>
        <p style='color:white; margin:0;'>NIFTY | BANK NIFTY | STOCKS | ERROR FREE v2.0</p>
    </div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("🔍 Select Asset")
    asset = st.selectbox("Market:", ["^NSEI", "^NSEBANK", "SBIN.NS", "RELIANCE.NS"])
    st.info("Note: Market Hours (9:15 AM - 3:30 PM)")

if st.button("📢 ACTIVATE JARVIS VOICE", use_container_width=True):
    jarvis_speak("Indian Market Jarvis is online. Waiting for signal.")

if "last_sig" not in st.session_state: st.session_state.last_sig = ""

# --- 🚀 5. EXECUTION ---
df = get_nse_data(asset)

# ERROR FIX: Check if enough data exists before calculation
if not df.empty and len(df) > 21:
    ltp = round(df['Close'].iloc[-1], 2)
    
    # Fast Calculation
    df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
    df['E200'] = df['Close'].ewm(span=200, adjust=False).mean()

    buy_sig = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (ltp > df['E200'].iloc[-1])
    sell_sig = (df['E9'].iloc[-1] < df['E21'].iloc[-1]) and (ltp < df['E200'].iloc[-1])

    if buy_sig and st.session_state.last_sig != "BUY":
        st.session_state.last_sig = "BUY"
        jarvis_speak(f"Rajveer Sir, Call Signal at {ltp}.")
    elif sell_sig and st.session_state.last_sig != "SELL":
        st.session_state.last_sig = "SELL"
        jarvis_speak(f"Rajveer Sir, Put Signal at {ltp}.")

    # Dashboard Display
    c1, c2 = st.columns([2, 1])
    with c1:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.metric("LTP", f"₹{ltp}")
        st.info(f"SIGNAL: {st.session_state.last_sig if st.session_state.last_sig else 'SCANNING'}")
else:
    st.warning("📡 बाज़ार अभी बंद है या डेटा लोड हो रहा है। जार्विस सोमवार सुबह 9:15 पर ऑटोमैटिक शुरू हो जाएगा।")
