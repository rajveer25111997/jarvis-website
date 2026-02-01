import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- 🎯 1. BUDGET SESSION CONFIG ---
st.set_page_config(page_title="JARVIS-R: BUDGET LIVE", layout="wide")
st_autorefresh(interval=2000, key="budget_v5_fix") # 2 Seconds Ultra-Fast

# --- 🧠 2. EMERGENCY DATA ENGINE ---
def get_live_nse_data(symbol):
    try:
        # बजट के दिन डेटा लैग कम करने के लिए 'fast_info' का इस्तेमाल
        tk = yf.Ticker(symbol)
        # 1-दिन का 1-मिनट डेटा
        df = tk.history(period="1d", interval="1m", prepost=True)
        if not df.empty:
            return df
        # अगर 1d फेल हो तो 5d का लेटेस्ट लें
        return tk.history(period="5d", interval="1m").tail(100)
    except:
        return pd.DataFrame()

# --- 🔊 3. VOICE ENGINE ---
def jarvis_speak(text):
    js = f"<script>var m=new SpeechSynthesisUtterance('{text}');window.speechSynthesis.speak(m);</script>"
    st.components.v1.html(js, height=0)

# --- 🏦 4. BRANDING ---
st.markdown(f"""
    <div style='text-align:center; background:linear-gradient(90deg, #ff9933, #ffffff, #128807); padding:10px; border-radius:15px; border:2px solid blue;'>
        <h2 style='color:blue; margin:0;'>🤖 JARVIS-R: BUDGET LIVE TRACKER</h2>
        <p style='color:black; margin:0;'>LIVE TIME: {datetime.now().strftime('%H:%M:%S')}</p>
    </div>
""", unsafe_allow_html=True)

if st.button("📢 ACTIVATE VOICE (सिग्नल के लिए दबाएं)"):
    jarvis_speak("Budget Live Monitoring Active Rajveer Sir.")

# --- 🚀 5. EXECUTION ---
asset = st.sidebar.selectbox("Market Asset:", ["^NSEI", "^NSEBANK", "SBIN.NS", "RELIANCE.NS"])
df = get_live_nse_data(asset)

if not df.empty:
    ltp = round(df['Close'].iloc[-1], 2)
    df['E9'] = df['Close'].ewm(span=9).mean()
    df['E21'] = df['Close'].ewm(span=21).mean()
    df['E200'] = df['Close'].ewm(span=200).mean()

    # --- 🚦 SIGNALS ---
    buy_sig = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (ltp > df['E200'].iloc[-1])
    sell_sig = (df['E9'].iloc[-1] < df['E21'].iloc[-1]) and (ltp < df['E200'].iloc[-1])

    c1, c2 = st.columns([2, 1])
    with c1:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.add_trace(go.Scatter(x=df.index, y=df['E200'], name='200 EMA', line=dict(color='orange', width=2)))
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.metric(f"{asset} PRICE", f"₹{ltp}", delta=f"{round(ltp - df['Open'].iloc[0], 2)}")
        if buy_sig:
            st.success("🟢 CALL SIGNAL: BULLISH MOVE")
            if "last" not in st.session_state or st.session_state.last != "BUY":
                jarvis_speak("Rajveer Sir, Call entry detected.")
                st.session_state.last = "BUY"
        elif sell_sig:
            st.error("🔴 PUT SIGNAL: BEARISH MOVE")
            if "last" not in st.session_state or st.session_state.last != "SELL":
                jarvis_speak("Rajveer Sir, Put entry detected.")
                st.session_state.last = "SELL"
        else:
            st.info("⌛ SCANNING... NO SIGNAL")
else:
    st.error("📡 डेटा अभी भी नहीं मिल रहा। कृपया Symbol बदलें या Internet चेक करें।")
