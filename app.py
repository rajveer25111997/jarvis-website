import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- 🎯 1. SETTINGS ---
st.set_page_config(page_title="Jarvis: NSE Master", layout="wide")
st_autorefresh(interval=2000, key="jarvis_nse_final")

# --- 🔊 2. SIREN & WAKE SYSTEM ---
def jarvis_emergency_system(text):
    siren_url = "https://www.soundjay.com/buttons/sounds/beep-09.mp3"
    js_code = f"""
    <script>
    if ('wakeLock' in navigator) {{ navigator.wakeLock.request('screen').catch(err => {{}}); }}
    window.speechSynthesis.cancel();
    var siren = new Audio('{siren_url}');
    siren.play();
    setTimeout(function() {{
        var msg = new SpeechSynthesisUtterance('{text}');
        msg.lang = 'hi-IN';
        window.speechSynthesis.speak(msg);
    }}, 1200);
    </script>
    """
    st.components.v1.html(js_code, height=0)

st.markdown("<h1 style='text-align:center; color:#007BFF;'>🛡️ JARVIS: NSE STOCK STATION v42.0</h1>", unsafe_allow_html=True)

# State Management
if "st_last" not in st.session_state: st.session_state.st_last = ""
if "st_entry" not in st.session_state: st.session_state.st_entry = 0.0

# --- 🧠 3. NSE DATA ENGINE ---
asset = st.sidebar.selectbox("Select NSE Asset:", ["^NSEI", "^NSEBANK", "SBIN.NS", "RELIANCE.NS"])

def get_nse_data(symbol):
    try:
        # EMA200 के लिए कम से कम 5 दिन का डेटा माँगना ज़रूरी है
        df = yf.download(symbol, period="5d", interval="1m", progress=False)
        return df
    except: return pd.DataFrame()

df = get_nse_data(asset)

# ERROR PROTECTION: Check if enough data is available
if not df.empty and len(df) > 200:
    try:
        # Indicators Calculation (Manual to avoid library errors)
        df['E9'] = df['Close'].ewm(span=9).mean()
        df['E21'] = df['Close'].ewm(span=21).mean()
        df['E200'] = df['Close'].ewm(span=200).mean()

        ltp = float(df['Close'].iloc[-1])
        e9 = float(df['E9'].iloc[-1])
        e21 = float(df['E21'].iloc[-1])
        e200 = float(df['E200'].iloc[-1])

        # --- 🚦 SIGNALS (Robust Comparison) ---
        is_call = bool(e9 > e21 and ltp > e200)
        is_put = bool(e9 < e21 and ltp < e200)

        # Signal Trigger with Siren
        if is_call and st.session_state.st_last != "CALL":
            st.session_state.st_last = "CALL"; st.session_state.st_entry = ltp
            jarvis_emergency_system(f"राजवीर सर, {asset} में कॉल सिग्नल मिला है। जाग जाइये!")
        elif is_put and st.session_state.st_last != "PUT":
            st.session_state.st_last = "PUT"; st.session_state.st_entry = ltp
            jarvis_emergency_system(f"राजवीर सर, {asset} में पुट सिग्नल मिला है। बाज़ार गिर रहा है!")

        # --- 📺 DASHBOARD ---
        c1, c2, c3 = st.columns(3)
        c1.metric(f"LIVE {asset}", f"₹{round(ltp, 2)}")
        c2.metric("SIGNAL", st.session_state.st_last if st.session_state.st_last else "SCANNING")
        pnl = round(ltp - st.session_state.st_entry if st.session_state.st_last == "CALL" else st.session_state.st_entry - ltp, 2) if st.session_state.st_entry > 0 else 0
        c3.metric("PNL POINTS", f"{pnl} Pts")

        # Chart
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.add_trace(go.Scatter(x=df.index, y=df['E200'], name='200 EMA', line=dict(color='orange')))
        fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.info("📡 Calculating Indicators... Waiting for Data Stability.")
else:
    st.warning("📡 Connecting to Market... Need more data points for 200 EMA.")

if st.button("🔄 Reset Manual"):
    st.session_state.st_last = ""; st.session_state.st_entry = 0.0; st.rerun()
