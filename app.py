import streamlit as st
import pandas as pd
import pandas_ta as ta
import requests
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME CONFIG ---
st.set_page_config(page_title="Jarvis Magic v147", layout="wide")
st_autorefresh(interval=1000, key="jarvis_magic_v147")

def jarvis_speak(text):
    if text:
        js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang='hi-IN'; window.speechSynthesis.speak(m);</script> "
        st.components.v1.html(js, height=0)

# --- 🧠 2. PERMANENT BRAIN ---
if "init" not in st.session_state:
    st.session_state.update({
        "locked": False, "signal": "SCANNING", 
        "ep": 0.0, "sl": 0.0, "tg": 0.0,
        "advice": "Analyzing Market Forces..."
    })

st.markdown("<h1 style='text-align:center; color:#00FF00;'>⚡ JARVIS MAGIC ENGINE v147.0</h1>", unsafe_allow_html=True)

# --- 📈 3. THE NO-FAIL DATA FETCHER ---
def get_magic_data():
    try:
        # सीधा रास्ता - No yfinance Library needed
        url = "https://query1.finance.yahoo.com/v8/finance/chart/^NSEI?interval=1m&range=1d"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5).json()
        r = res['chart']['result'][0]
        p = r['indicators']['quote'][0]['close']
        t = r['timestamp']
        df = pd.DataFrame({'Close': p}, index=pd.to_datetime(t, unit='s')).dropna()
        return df
    except:
        return pd.DataFrame()

df = get_magic_data()

# --- ⚙️ 4. THE BRAIN LOGIC ---
if not df.empty and len(df) > 5:
    ltp = round(df['Close'].iloc[-1], 2)
    
    # जावेद-करिश्मा स्ट्रैटेजी (EMA 9/21)
    df['E9'] = ta.ema(df['Close'], length=9)
    df['E21'] = ta.ema(df['Close'], length=21)
    
    # जार्विस की सुरक्षा (Error Shield)
    e9 = df['E9'].iloc[-1] if not pd.isna(df['E9'].iloc[-1]) else 0
    e21 = df['E21'].iloc[-1] if not pd.isna(df['E21'].iloc[-1]) else 0

    if not st.session_state.locked:
        if e9 > e21 and e21 != 0:
            st.session_state.update({"signal": "CALL", "ep": ltp, "sl": ltp-40, "tg": ltp+150, "locked": True, "advice": "RUKO (Big Profit)"})
            jarvis_speak("नमस्ते राजवीर सर, कॉल सिग्नल लॉक कर दिया गया है।")
        elif e9 < e21 and e21 != 0:
            st.session_state.update({"signal": "PUT", "ep": ltp, "sl": ltp+40, "tg": ltp-150, "locked": True, "advice": "RUKO (Giraavat)"})
            jarvis_speak("नमस्ते राजवीर सर, पुट सिग्नल लॉक कर दिया गया है।")

    # --- 📊 5. DASHBOARD ---
    c1, c2, c3 = st.columns(3)
    c1.metric("NIFTY 50", f"₹{ltp}")
    c2.success(f"📌 {st.session_state.signal} @ {st.session_state.ep}")
    
    # Advice Box
    status_clr = "gold" if "RUKO" in st.session_state.advice else "#00FF00"
    c3.markdown(f"<div style='background-color:{status_clr}; padding:10px; border-radius:10px; color:black; font-weight:bold; text-align:center;'>JARVIS: {st.session_state.advice}</div>", unsafe_allow_html=True)

    # Chart
    fig = go.Figure(data=[go.Scatter(x=df.index, y=df['Close'], line=dict(color='#00FF00', width=2))])
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("📡 जार्विस बाज़ार के 'बड़े खिलाड़ियों' से डेटा खींच रहा है... बस कुछ सेकंड।")

if st.button("🔄 RESET JARVIS"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()
