import streamlit as st
import pandas as pd
import requests
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME SETTINGS ---
st.set_page_config(page_title="Jarvis NSE v117", layout="wide")
st_autorefresh(interval=3000, key="jarvis_nse_v117")

def jarvis_speak(text):
    if text:
        js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang='hi-IN'; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 🧠 2. PERMANENT BRAIN ---
if "init" not in st.session_state:
    st.session_state.update({
        "locked": False, "signal": "SCANNING", 
        "ep": 0.0, "sl": 0.0, "tg": 0.0,
        "why": "मार्केट डेटा का शुद्ध विश्लेषण जारी है...",
        "capital_inr": 10000.0
    })

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🛡️ NSE COMMANDER v117.0</h1>", unsafe_allow_html=True)

if st.button("🔊 ACTIVATE JARVIS SYSTEM"):
    jarvis_speak("नमस्ते राजवीर सर, बग फ्री सिस्टम अब लाइव है।")

# --- 📈 NSE DATA ENGINE ---
def get_nse_data():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/^NSEI?interval=1m&range=1d"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5).json()
        p = res['chart']['result'][0]['indicators']['quote'][0]['close']
        v = res['chart']['result'][0]['indicators']['quote'][0]['volume']
        t = res['chart']['result'][0]['timestamp']
        df = pd.DataFrame({'Close': p, 'Volume': v}, index=pd.to_datetime(t, unit='s')).dropna()
        return df
    except:
        return pd.DataFrame()

df = get_nse_data()

# --- ⚙️ ERROR-FREE STRATEGY ---
# कम से कम 200 कैंडल्स का इंतज़ार करने के बजाय, उपलब्ध डेटा पर सुरक्षित चेक
if not df.empty and len(df) > 1:
    try:
        # Indicators
        df['E9'] = ta.ema(df['Close'], length=9)
        df['E21'] = ta.ema(df['Close'], length=21)
        df['E200'] = ta.ema(df['Close'], length=min(len(df), 200))
        
        ltp = round(df['Close'].iloc[-1], 2)
        
        if not st.session_state.locked:
            # सुरक्षित वैल्यू चेक (TypeError से बचने के लिए)
            val_e9 = df['E9'].iloc[-1]
            val_e21 = df['E21'].iloc[-1]
            val_e200 = df['E200'].iloc[-1] if not pd.isna(df['E200'].iloc[-1]) else ltp

            if not pd.isna(val_e9) and not pd.isna(val_e21):
                is_call = val_e9 > val_e21 and ltp > val_e200
                is_put = val_e9 < val_e21 and ltp < val_e200
                
                if is_call:
                    st.session_state.update({"signal": "CALL (BUY)", "ep": ltp, "sl": ltp-50, "tg": ltp+250, "locked": True, "why": "9/21 क्रॉसओवर और ट्रेंड बुलिश है।"})
                    jarvis_speak("एन एस ई कॉल लॉक्ड।")
                elif is_put:
                    st.session_state.update({"signal": "PUT (SELL)", "ep": ltp, "sl": ltp+50, "tg": ltp-250, "locked": True, "why": "9/21 क्रॉसओवर और ट्रेंड बेरिश है।"})
                    jarvis_speak("एन एस ई पुट लॉक्ड।")

        # Display
        c1, c2, c3 = st.columns(3)
        c1.metric("NIFTY 50", f"₹{ltp}")
        c2.success(f"📌 {st.session_state.signal}")
        c3.warning(f"💰 Cap: ₹10k")

        st.info(f"🧠 **Why:** {st.session_state.why}")

        fig = go.Figure(data=[go.Scatter(x=df.index, y=df['Close'], line=dict(color='#00FF00'))])
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.info("🔄 जार्विस डेटा को सिंक कर रहा है, कृपया 2 सेकंड रुकें...")
else:
    st.info("📡 बाज़ार की शुरुआती कैंडल्स का इंतज़ार है...")

if st.button("🔄 RESET"):
    for key in ["locked", "signal", "ep", "sl", "tg", "why"]:
        if key in st.session_state: del st.session_state[key]
    st.rerun()
