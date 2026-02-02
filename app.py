import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- 🎯 1. BUDGET SESSION CONFIG ---
st.set_page_config(page_title="JARVIS-R: BUDGET LIVE PRO", layout="wide")
st_autorefresh(interval=2000, key="budget_v38_final")

# --- 🔊 2. EMERGENCY SIREN & WAKE SYSTEM ---
def jarvis_emergency_system(text):
    siren_url = "https://www.soundjay.com/buttons/sounds/beep-09.mp3"
    js_code = f"""
    <script>
    // स्क्रीन को सोने से रोकना
    if ('wakeLock' in navigator) {{
        navigator.wakeLock.request('screen').catch(err => {{}});
    }}
    window.speechSynthesis.cancel();
    // तेज़ सायरन बजाना
    var siren = new Audio('{siren_url}');
    siren.volume = 1.0;
    siren.play();
    // जार्विस की आवाज़
    setTimeout(function() {{
        var msg = new SpeechSynthesisUtterance('{text}');
        msg.lang = 'hi-IN';
        msg.rate = 1.0;
        window.speechSynthesis.speak(msg);
    }}, 1200);
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 🧠 3. EMERGENCY DATA ENGINE ---
def get_live_nse_data(symbol):
    try:
        tk = yf.Ticker(symbol)
        df = tk.history(period="1d", interval="1m", prepost=True)
        if not df.empty: return df
        return tk.history(period="5d", interval="1m").tail(100)
    except: return pd.DataFrame()

# --- 🎨 4. BRANDING ---
st.markdown(f"""
<div style='text-align:center; background:linear-gradient(90deg, #ff9933, #ffffff, #128807); padding:10px; border-radius:15px; border:2px solid blue;'>
    <h2 style='color:blue; margin:0;'>🤖 JARVIS-R: NEVER-SLEEP STOCK STATION</h2>
    <p style='color:black; margin:0;'>LIVE TIME: {datetime.now().strftime('%H:%M:%S')}</p>
</div>
""", unsafe_allow_html=True)

# State Management for Signals & Tracking
if "last" not in st.session_state: st.session_state.last = ""
if "e_p" not in st.session_state: st.session_state.e_p = 0.0

if st.button("📢 ACTIVATE JARVIS (सिग्नल के लिए दबाएं)"):
    jarvis_emergency_system("Budget monitoring active, Rajveer Sir. I will wake you up on every signal.")

# --- 🚀 5. EXECUTION ---
asset = st.sidebar.selectbox("Market Asset:", ["^NSEI", "^NSEBANK", "SBIN.NS", "RELIANCE.NS"])
df = get_live_nse_data(asset)

if not df.empty:
    ltp = round(df['Close'].iloc[-1], 2)
    df['E9'] = ta.ema(df['Close'], length=9)
    df['E21'] = ta.ema(df['Close'], length=21)
    df['E200'] = ta.ema(df['Close'], length=200)

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
            st.success("🟢 CALL SIGNAL: BULLISH")
            if st.session_state.last != "BUY":
                jarvis_emergency_system(f"Rajveer Sir, {asset} me Call entry detect hui hai. Jaag jaaiye!")
                st.session_state.last = "BUY"
                st.session_state.e_p = ltp
        elif sell_sig:
            st.error("🔴 PUT SIGNAL: BEARISH")
            if st.session_state.last != "SELL":
                jarvis_emergency_system(f"Rajveer Sir, {asset} me Put entry detect hui hai. Turant check kijiye!")
                st.session_state.last = "SELL"
                st.session_state.e_p = ltp
        else:
            st.info("⌛ SCANNING... NO SIGNAL")

    # Tracking PNL if in trade
    if st.session_state.e_p > 0:
        pnl = round(ltp - st.session_state.e_p if st.session_state.last == "BUY" else st.session_state.e_p - ltp, 2)
        st.sidebar.metric("Live Trade PNL", f"{pnl} Pts")
else:
    st.error("📡 डेटा नहीं मिल रहा। कृपया इंटरनेट चेक करें।")

if st.button("🔄 Reset System"):
    st.session_state.last = ""; st.session_state.e_p = 0.0; st.rerun()
