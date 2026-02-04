import streamlit as st
import pandas as pd
import pandas_ta as ta
import requests
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME SETTINGS (1s Refresh) ---
st.set_page_config(page_title="Jarvis v145", layout="wide")
st_autorefresh(interval=1000, key="jarvis_v145_final")

# --- 🔊 2. BROWSER VOICE FIX ---
def jarvis_speak(text):
    if text:
        js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang='hi-IN'; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 🧠 3. PERMANENT STATE ---
if "init" not in st.session_state:
    st.session_state.update({"lock": False, "sig": "SCANNING", "ep": 0.0, "advice": "डेटा सिंक हो रहा है..."})

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🏛️ JARVIS UNSTOPPABLE v145.0</h1>", unsafe_allow_html=True)

# --- 📈 4. DATA ENGINE (No-Error Logic) ---
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

# --- ⚙️ 5. SAFETY CHECK & STRATEGY ---
# यहाँ हमने चेक लगाया है ताकि TypeError न आए
if not df.empty and len(df) > 25:
    try:
        df['E9'] = ta.ema(df['Close'], length=9)
        df['E21'] = ta.ema(df['Close'], length=21)
        # अगर 200 कैंडल नहीं हैं, तो यह उपलब्ध डेटा का औसत लेगा (Safety Guard)
        df['E200'] = ta.ema(df['Close'], length=min(len(df), 200))
        
        ltp = round(df['Close'].iloc[-1], 2)

        if not st.session_state.lock:
            # 9/21 और 200 EMA का शुद्ध संगम
            if df['E9'].iloc[-1] > df['E21'].iloc[-1] and ltp > df['E200'].iloc[-1]:
                st.session_state.update({"sig": "CALL", "ep": ltp, "lock": True, "advice": "RUKO (BIG MOVE)"})
                jarvis_speak("एन एस ई कॉल लॉक्ड। राजवीर सर, बड़े खिलाड़ियों की चाल शुरू हुई है।")
            elif df['E9'].iloc[-1] < df['E21'].iloc[-1] and ltp < df['E200'].iloc[-1]:
                st.session_state.update({"sig": "PUT", "ep": ltp, "lock": True, "advice": "RUKO (FALLING)"})
                jarvis_speak("एन एस ई पुट लॉक्ड। ऑपरेटर्स माल बेच रहे हैं।")

        # Dashboard
        c1, c2 = st.columns(2)
        c1.metric("NIFTY 50", f"₹{ltp}")
        c2.success(f"📌 {st.session_state.sig} @ {st.session_state.ep}")
        
        st.info(f"🧠 **Jarvis Advice:** {st.session_state.advice}")

        fig = go.Figure(data=[go.Scatter(x=df.index, y=df['Close'], line=dict(color='#00FF00'))])
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning("जार्विस डेटा प्रोसेस कर रहा है... कृपया रुकें।")
else:
    st.info("📡 मार्केट अभी खुला है, जार्विस पर्याप्त डेटा (25 कैंडल्स) जमा कर रहा है ताकि एरर न आए।")

if st.button("🔄 RESET ALL"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()
