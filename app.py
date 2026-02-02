import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- 🎯 1. SETTINGS ---
st.set_page_config(page_title="Jarvis: Stock Master", layout="wide")
st_autorefresh(interval=2000, key="jarvis_nse_live")

# --- 🔊 2. SIREN & WAKE SYSTEM (आवाज़ और सायरन) ---
def jarvis_emergency_system(text):
    siren_url = "https://www.soundjay.com/buttons/sounds/beep-09.mp3"
    js_code = f"""
    <script>
    // स्क्रीन को चालू रखने के लिए
    if ('wakeLock' in navigator) {{ navigator.wakeLock.request('screen'); }}
    window.speechSynthesis.cancel();
    // सायरन
    var siren = new Audio('{siren_url}');
    siren.play();
    // जार्विस की आवाज़
    setTimeout(function() {{
        var msg = new SpeechSynthesisUtterance('{text}');
        msg.lang = 'hi-IN';
        window.speechSynthesis.speak(msg);
    }}, 1200);
    </script>
    """
    st.components.v1.html(js_code, height=0)

st.markdown("<h1 style='text-align:center; color:#007BFF;'>📈 JARVIS: NSE STOCK STATION</h1>", unsafe_allow_html=True)

# State Management
if "st_last" not in st.session_state: st.session_state.st_last = ""
if "st_entry" not in st.session_state: st.session_state.st_entry = 0.0

# --- 🧠 3. NSE DATA ENGINE ---
# यहाँ आप सिम्बल बदल सकते हैं
asset = st.sidebar.selectbox("Select NSE Asset:", ["^NSEI", "^NSEBANK", "SBIN.NS", "RELIANCE.NS", "TATASTEEL.NS"])

def get_nse_data(symbol):
    try:
        # 1 मिनट की कैंडल के साथ भारतीय बाज़ार का डेटा
        df = yf.download(symbol, period="1d", interval="1m", progress=False)
        return df
    except: return pd.DataFrame()

df = get_nse_data(asset)

if not df.empty and len(df) > 10:
    # --- 📊 INDICATORS (No External Library Needed) ---
    ltp = round(df['Close'].iloc[-1], 2)
    df['E9'] = df['Close'].ewm(span=9).mean()
    df['E21'] = df['Close'].ewm(span=21).mean()
    df['E200'] = df['Close'].ewm(span=200).mean()

    # --- 🚦 SIGNALS (9/21 Cross + 200 EMA Filter) ---
    is_call = bool(df['E9'].iloc[-1] > df['E21'].iloc[-1] and ltp > df['E200'].iloc[-1])
    is_put = bool(df['E9'].iloc[-1] < df['E21'].iloc[-1] and ltp < df['E200'].iloc[-1])

    # Trigger Alert
    if is_call and st.session_state.st_last != "CALL":
        st.session_state.st_last = "CALL"; st.session_state.st_entry = ltp
        jarvis_emergency_system(f"Rajveer Sir, {asset} में Call entry बनी है। सायरन बज गया है, चेक करें!")
    elif is_put and st.session_state.st_last != "PUT":
        st.session_state.st_last = "PUT"; st.session_state.st_entry = ltp
        jarvis_emergency_system(f"Rajveer Sir, {asset} में Put entry बनी है। बाज़ार गिर रहा है, उठ जाइये!")

    # --- 📺 DASHBOARD ---
    c1, c2, c3 = st.columns(3)
    c1.metric(f"LIVE {asset}", f"₹{ltp}")
    c2.metric("CURRENT SIGNAL", st.session_state.st_last if st.session_state.st_last else "SCANNING")
    pnl = round(ltp - st.session_state.st_entry if st.session_state.st_last == "CALL" else st.session_state.st_entry - ltp, 2) if st.session_state.st_entry > 0 else 0
    c3.metric("POINTS PNL", f"{pnl} Pts")

    # Full Chart
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.add_trace(go.Scatter(x=df.index, y=df['E200'], name='200 EMA', line=dict(color='orange', width=2)))
    fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("📡 NSE डेटा कनेक्ट हो रहा है... कृपया बाज़ार खुलने का इंतज़ार करें।")

if st.button("🔄 Reset Stock Jarvis"):
    st.session_state.st_last = ""; st.session_state.st_entry = 0.0; st.rerun()
