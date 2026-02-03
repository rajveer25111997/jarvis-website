import streamlit as st
import pandas as pd
import requests
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME SETTINGS ---
st.set_page_config(page_title="Jarvis NSE Master", layout="wide")
st_autorefresh(interval=3000, key="jarvis_v110_final")

# --- 🔊 2. MASTER VOICE ENGINE ---
def jarvis_speak(text):
    if text:
        js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang='hi-IN'; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 🧠 3. STATE MANAGEMENT ---
if "init" not in st.session_state:
    st.session_state.update({"lock": False, "sig": "SCANNING", "ep": 0.0, "sl": 0.0, "tg": 0.0, "why": "विश्लेषण जारी है..."})

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🛡️ JARVIS NSE MASTER v110.0</h1>", unsafe_allow_html=True)

if st.button("🔊 ACTIVATE VOICE (आवाज़ चालू करें)"):
    jarvis_speak("नमस्ते राजवीर सर, स्टॉक मार्केट मास्टर सिस्टम अब लाइव है।")

# --- 📈 DATA ENGINE (Triple Backup Logic) ---
def get_live_data():
    try:
        # रास्ता 1: Direct JSON Feed
        url = "https://query1.finance.yahoo.com/v8/finance/chart/^NSEI?interval=1m&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=5).json()
        p = res['chart']['result'][0]['indicators']['quote'][0]['close']
        t = res['chart']['result'][0]['timestamp']
        df = pd.DataFrame({'Close': p}, index=pd.to_datetime(t, unit='s'))
        return df.dropna()
    except:
        return pd.DataFrame()

df = get_live_data()

if not df.empty:
    # Indicators (Javed Strategy 9/21)
    df['E9'] = ta.ema(df['Close'], length=9)
    df['E21'] = ta.ema(df['Close'], length=21)
    df['E200'] = ta.ema(df['Close'], length=200)
    ltp = round(df['Close'].iloc[-1], 2)

    if not st.session_state.lock:
        # BRAIN LOGIC
        is_call = df['E9'].iloc[-1] > df['E21'].iloc[-1] and ltp > df['E200'].iloc[-1]
        is_put = df['E9'].iloc[-1] < df['E21'].iloc[-1] and ltp < df['E200'].iloc[-1]
        
        if is_call:
            st.session_state.update({"sig": "CALL", "ep": ltp, "sl": ltp-50, "tg": ltp+250, "lock": True, "why": "9/21 क्रॉसओवर और 200 EMA के ऊपर मजबूत सपोर्ट मिला है।"})
            jarvis_speak("एन एस ई कॉल लॉक्ड")
        elif is_put:
            st.session_state.update({"sig": "PUT", "ep": ltp, "sl": ltp+50, "tg": ltp-250, "lock": True, "why": "बिकवाली का दबाव है और भाव 200 EMA के नीचे गिर रहा है।"})
            jarvis_speak("एन एस ई पुट लॉक्ड")

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("NIFTY 50", f"₹{ltp}")
    c2.success(f"📌 {st.session_state.sig} | E: {st.session_state.ep}")
    c3.warning(f"🎯 TG: {st.session_state.tg}")

    st.info(f"🧠 **Jarvis Why:** {st.session_state.why}")

    # Chart
    fig = go.Figure(data=[go.Scatter(x=df.index, y=df['Close'], line=dict(color='#00FF00', width=2))])
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("📡 डेटा इंतज़ार में है... कृपया रिफ्रेश करें।")

if st.button("🔄 RESET SYSTEM"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()
