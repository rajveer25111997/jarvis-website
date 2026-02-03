import streamlit as st
import pandas as pd
import pandas_ta as ta
import requests
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME CONFIG ---
st.set_page_config(page_title="Jarvis Stock Master", layout="wide")
st_autorefresh(interval=3000, key="jarvis_nse_final")

# --- 🔊 2. MASTER VOICE ENGINE ---
def jarvis_speak(text):
    if text:
        js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang='hi-IN'; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 🧠 3. PERMANENT STATE (Brain & Lock Management) ---
if "init" not in st.session_state:
    st.session_state.update({
        "locked": False,
        "signal": "SCANNING",
        "why": "बाजार के मूड और डेटा का विश्लेषण कर रहा हूँ...",
        "ep": 0.0, "sl": 0.0, "tg": 0.0
    })

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🛡️ JARVIS STOCK COMMANDER v108.0</h1>", unsafe_allow_html=True)

# Activation Button
if st.button("🔊 ACTIVATE JARVIS VOICE"):
    jarvis_speak("नमस्ते राजवीर सर, स्टॉक मार्केट मास्टर सिस्टम अब लाइव है।")

# --- 📈 DATA ENGINE (Triple Backup Logic) ---
try:
    # Source: High-Speed Finance API
    url = "https://query1.finance.yahoo.com/v8/finance/chart/^NSEI?interval=1m&range=1d"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers, timeout=5).json()
    
    price_data = res['chart']['result'][0]['indicators']['quote'][0]['close']
    time_data = res['chart']['result'][0]['timestamp']
    
    df = pd.DataFrame({'Close': price_data}, index=pd.to_datetime(time_data, unit='s'))
    df = df.dropna()

    if not df.empty:
        # Indicators Combination
        df['E9'] = ta.ema(df['Close'], length=9)
        df['E21'] = ta.ema(df['Close'], length=21)
        df['E200'] = ta.ema(df['Close'], length=200)
        df['ATR'] = ta.atr(df.index.to_series(), df['Close'], df['Close'], length=14) # Proxy for News Volatility
        
        ltp = round(df['Close'].iloc[-1], 2)

        # --- JARVIS BRAIN & LOCKING ---
        if not st.session_state.locked:
            is_call = df['E9'].iloc[-1] > df['E21'].iloc[-1] and ltp > df['E200'].iloc[-1]
            is_put = df['E9'].iloc[-1] < df['E21'].iloc[-1] and ltp < df['E200'].iloc[-1]
            
            if is_call:
                st.session_state.update({
                    "signal": "CALL", "ep": ltp, "sl": ltp-50, "tg": ltp+250, "locked": True,
                    "why": "मार्केट में बुलिश पावर है। 9/21 क्रॉसओवर और 200 EMA के ऊपर मजबूत सपोर्ट मिला है।"
                })
                jarvis_speak("एन एस ई कॉल सिग्नल लॉक्ड। बाजार ऊपर जाने के लिए तैयार है।")
            elif is_put:
                st.session_state.update({
                    "signal": "PUT", "ep": ltp, "sl": ltp+50, "tg": ltp-250, "locked": True,
                    "why": "बिकवाली का दबाव है। 9/21 नीचे की ओर मुड़ा है और भाव 200 EMA के नीचे गिर रहा है।"
                })
                jarvis_speak("एन एस ई पुट सिग्नल लॉक्ड। बाजार में गिरावट की संभावना है।")

        # --- DISPLAY SECTION ---
        col1, col2, col3 = st.columns(3)
        col1.metric("NIFTY 50 LIVE", f"₹{ltp}")
        col2.success(f"📌 {st.session_state.signal} LOCKED")
        col3.warning(f"🎯 TARGET: {st.session_state.tg}")

        st.info(f"🧠 **Jarvis Why (कारण):** {st.session_state.why}")

        # Charts
        fig = go.Figure(data=[go.Scatter(x=df.index, y=df['Close'], name='Price', line=dict(color='#00FF00', width=2))])
        fig.add_trace(go.Scatter(x=df.index, y=df['E9'], name='EMA 9', line=dict(color='yellow', width=1)))
        fig.add_trace(go.Scatter(x=df.index, y=df['E21'], name='EMA 21', line=dict(color='red', width=1)))
        
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)
        
        st.write(f"**LOCKED ENTRY:** {st.session_state.ep} | **STOP LOSS:** {st.session_state.sl}")

except Exception as e:
    st.info("🔄 जार्विस स्टॉक डेटा से जुड़ने की कोशिश कर रहा है... कृपया 5 सेकंड रुकें।")

# --- 🛡️ MASTER SYSTEM RESET ---
st.write("---")
if st.button("🔄 CLEAR & SCAN NEXT TRADE"):
    for key in ["locked", "signal", "why", "ep", "sl", "tg"]:
        if key in st.session_state: del st.session_state[key]
    st.rerun()
