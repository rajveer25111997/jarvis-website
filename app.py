import streamlit as st
import pandas as pd
import pandas_ta as ta
import requests
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SETTINGS ---
st.set_page_config(page_title="Jarvis v146", layout="wide")
st_autorefresh(interval=2000, key="jarvis_v146")

# --- 🔊 2. VOICE FIX ---
def jarvis_speak(text):
    if text:
        js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang='hi-IN'; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 🧠 3. STATE ---
if "init" not in st.session_state:
    st.session_state.update({"lock": False, "sig": "SCANNING", "ep": 0.0, "advice": "इंतज़ार करें..."})

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🛡️ JARVIS UNSTOPPABLE v146.0</h1>", unsafe_allow_html=True)

# --- 📈 4. DATA ENGINE (With Safety Guard) ---
def get_data():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/^NSEI?interval=1m&range=1d"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5).json()
        r = res['chart']['result'][0]
        p = r['indicators']['quote'][0]['close']
        t = r['timestamp']
        df = pd.DataFrame({'Close': p}, index=pd.to_datetime(t, unit='s')).dropna()
        return df
    except: return pd.DataFrame()

df = get_data()

# --- ⚙️ 5. NO-CRASH LOGIC ---
# कम से कम 30 कैंडल्स होने पर ही जार्विस काम शुरू करेगा
if not df.empty and len(df) > 30:
    try:
        df['E9'] = ta.ema(df['Close'], length=9)
        df['E21'] = ta.ema(df['Close'], length=21)
        # 200 EMA के लिए सुरक्षा: अगर 200 कैंडल्स नहीं हैं, तो यह उपलब्ध डेटा का अधिकतम लेगा
        df['E200'] = ta.ema(df['Close'], length=min(len(df), 200))
        
        ltp = round(df['Close'].iloc[-1], 2)

        if not st.session_state.lock:
            # सुरक्षित इंडेक्सिंग (TypeError Fix)
            val_e9 = df['E9'].iloc[-1]
            val_e21 = df['E21'].iloc[-1]
            val_e200 = df['E200'].iloc[-1] if not pd.isna(df['E200'].iloc[-1]) else ltp
            
            if val_e9 > val_e21 and ltp > val_e200:
                st.session_state.update({"sig": "CALL", "ep": ltp, "lock": True, "advice": "RUKO (PROFIT BUILDING)"})
                jarvis_speak("एन एस ई कॉल लॉक्ड। राजवीर सर, बाज़ार ऊपर जा रहा है।")
            elif val_e9 < val_e21 and ltp < val_e200:
                st.session_state.update({"sig": "PUT", "ep": ltp, "lock": True, "advice": "RUKO (GIRAAVAT)"})
                jarvis_speak("एन एस ई पुट लॉक्ड। बाज़ार नीचे गिर रहा है।")

        # Dashboard View
        c1, c2 = st.columns(2)
        c1.metric("NIFTY 50", f"₹{ltp}")
        c2.success(f"📌 {st.session_state.sig} | EP: {st.session_state.ep}")
        
        st.info(f"🧠 **Jarvis Advice:** {st.session_state.advice}")

        fig = go.Figure(data=[go.Scatter(x=df.index, y=df['Close'], line=dict(color='#00FF00'))])
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning("जार्विस डेटा प्रोसेस कर रहा है... कृपया 5 सेकंड रुकें।")
else:
    st.info("📡 मार्केट अभी खुला है। जार्विस पर्याप्त डेटा (30 कैंडल्स) जमा कर रहा है ताकि ऐप क्रैश न हो।")

if st.button("🔄 RESET ALL"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()
