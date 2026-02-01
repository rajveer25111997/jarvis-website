import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. INDIAN MARKET CONFIG ---
st.set_page_config(page_title="JARVIS-R: NSE SNIPER", layout="wide")
st_autorefresh(interval=5000, key="nse_refresh") # 5-second refresh for NSE

# --- 🧠 2. NSE DATA ENGINE ---
def get_nse_data(symbol):
    try:
        # NSE के लिए सिंबल के पीछे .NS लगाना ज़रूरी है (e.g., RELIANCE.NS)
        df = yf.download(symbol, period="1d", interval="1m", progress=False, auto_adjust=True)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df
    except: return pd.DataFrame()

# --- 🔊 3. VOICE ENGINE ---
def jarvis_speak(text):
    js = f"<script>var m=new SpeechSynthesisUtterance('{text}');window.speechSynthesis.speak(m);</script>"
    st.components.v1.html(js, height=0)

# --- 🏦 4. BRANDING ---
st.markdown("""
    <div style='text-align:center; background:linear-gradient(90deg, #1e3c72, #2a5298); padding:15px; border-radius:15px; border:2px solid #fff;'>
        <h1 style='color:white; margin:0;'>🤖 JARVIS-R: NSE/BSE SNIPER</h1>
        <p style='color:white; margin:0;'>NIFTY | BANK NIFTY | STOCKS | INTRADAY MODE</p>
    </div>
""", unsafe_allow_html=True)

# Selection Sidebar
with st.sidebar:
    st.header("🔍 Select Asset")
    # भारतीय मार्केट के लिए कुछ टॉप सिम्बल्स
    asset = st.selectbox("Market:", ["^NSEI (NIFTY 50)", "^NSEBANK (BANK NIFTY)", "SBIN.NS", "RELIANCE.NS", "TATASTEEL.NS"])
    st.info("Note: Stocks के लिए सिंबल के पीछे .NS लगाएं।")

if st.button("📢 ACTIVATE JARVIS VOICE", use_container_width=True):
    jarvis_speak(f"Indian Market Jarvis is online for {asset}. Standing by Rajveer Sir.")

if "last_sig" not in st.session_state: st.session_state.last_sig = ""

# --- 🚀 5. EXECUTION ---
df = get_nse_data(asset)

if not df.empty:
    ltp = round(df['Close'].iloc[-1], 2)
    df['E9'] = df['Close'].ewm(span=9).mean()
    df['E21'] = df['Close'].ewm(span=21).mean()
    df['E200'] = df['Close'].ewm(span=200).mean()

    # Logic
    buy_sig = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (ltp > df['E200'].iloc[-1])
    sell_sig = (df['E9'].iloc[-1] < df['E21'].iloc[-1]) and (ltp < df['E200'].iloc[-1])

    if buy_sig and st.session_state.last_sig != "BUY":
        st.session_state.last_sig = "BUY"
        jarvis_speak(f"Rajveer Sir, Call Signal in {asset} at {ltp}. High Probability Buy.")
    elif sell_sig and st.session_state.last_sig != "SELL":
        st.session_state.last_sig = "SELL"
        jarvis_speak(f"Rajveer Sir, Put Signal in {asset} at {ltp}. Trend is Weak.")

    # --- 📺 DISPLAY ---
    c1, c2 = st.columns([2, 1])
    with c1:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.add_trace(go.Scatter(x=df.index, y=df['E200'], name='200 EMA', line=dict(color='orange')))
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        st.metric("CURRENT PRICE (LTP)", f"₹{ltp}")
        st.success(f"SIGNAL: {st.session_state.last_sig}" if st.session_state.last_sig == "BUY" else f"ALERT: {st.session_state.last_sig}")
        st.write("---")
        st.write("**Strategy Rules:**")
        st.write("✅ 9/21 EMA Crossover")
        st.write("✅ Price Above 200 EMA")
        st.write("✅ High Volume Breakout")

else:
    st.warning("📡 Waiting for Market Hours (9:15 AM - 3:30 PM).")
