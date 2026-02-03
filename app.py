import streamlit as st
import pandas as pd
import requests
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SETTINGS & REFRESH ---
st.set_page_config(page_title="Jarvis Final Master", layout="wide")
st_autorefresh(interval=3000, key="jarvis_v115")

# --- 🔊 2. VOICE ENGINE ---
def jarvis_speak(text):
    if text:
        js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang='hi-IN'; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 🧠 3. STATE MANAGEMENT (Permanent Lock) ---
if "init" not in st.session_state:
    st.session_state.update({
        "lock": False, "sig": "SCANNING", 
        "ep": 0.0, "sl": 0.0, "tg": 0.0,
        "why": "मार्केट डेटा और बड़े खिलाड़ियों की चाल का विश्लेषण जारी है...",
        "balance": 120.0
    })

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🏛️ JARVIS FINAL MASTER v115.0</h1>", unsafe_allow_html=True)

if st.button("🔊 ACTIVATE JARVIS SYSTEM"):
    jarvis_speak("नमस्ते राजवीर सर, जार्विस का मुकम्मल सिस्टम अब लाइव है।")

# --- 📈 DATA ENGINE (NSE + CRYPTO BACKUP) ---
def get_safe_data():
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

df = get_safe_data()

# --- ⚙️ CORE BRAIN LOGIC ---
if not df.empty and len(df) > 20:
    df['E9'] = ta.ema(df['Close'], length=9)
    df['E21'] = ta.ema(df['Close'], length=21)
    df['E200'] = ta.ema(df['Close'], length=200)
    ltp = round(df['Close'].iloc[-1], 2)
    vol_now = df['Volume'].iloc[-1]
    avg_vol = df['Volume'].tail(15).mean()

    if not st.session_state.lock:
        # Javed (9/21) + Big Player (200 EMA) + Operator Entry (Volume)
        is_call = df['E9'].iloc[-1] > df['E21'].iloc[-1] and ltp > df['E200'].iloc[-1]
        is_put = df['E9'].iloc[-1] < df['E21'].iloc[-1] and ltp < df['E200'].iloc[-1]
        big_move = vol_now > (avg_vol * 1.2) # 20% extra volume means Operator

        if is_call and big_move:
            st.session_state.update({
                "sig": "CALL (BUY)", "ep": ltp, "sl": ltp-50, "tg": ltp+250, "lock": True,
                "why": "बड़े खिलाड़ियों (Operators) ने भारी खरीदारी की है। भाव 9/21 और 200 EMA के ऊपर मजबूत है।"
            })
            jarvis_speak("राजवीर सर, ऑपरेटर्स की एंट्री मिली है। एन एस ई कॉल सिग्नल लॉक्ड।")
        elif is_put and big_move:
            st.session_state.update({
                "sig": "PUT (SELL)", "ep": ltp, "sl": ltp+50, "tg": ltp-250, "lock": True,
                "why": "बड़ी कंपनियों में बिकवाली शुरू हुई है। ट्रेंड 200 EMA के नीचे गिर रहा है।"
            })
            jarvis_speak("राजवीर सर, मार्केट में माल बेचा जा रहा है। एन एस ई पुट सिग्नल लॉक्ड।")

    # --- 📊 DISPLAY DASHBOARD ---
    col1, col2, col3 = st.columns(3)
    col1.metric("NIFTY 50", f"₹{ltp}")
    col2.success(f"📌 {st.session_state.sig}")
    
    # Capital Logic ($120)
    qty = round((st.session_state.balance * 85) / ltp, 2) # Adjusted for NSE
    col3.warning(f"💰 Qty: {qty} | Cap: $120")

    st.info(f"🧠 **Jarvis Analysis (कारण):** {st.session_state.why}")

    # Candlestick Chart
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Close'], high=df['Close'], low=df['Close'], close=df['Close'], name='Price')])
    fig.add_trace(go.Scatter(x=df.index, y=df['E9'], name='Javed (9 EMA)', line=dict(color='yellow')))
    fig.add_trace(go.Scatter(x=df.index, y=df['E21'], name='Karishma (21 EMA)', line=dict(color='cyan')))
    fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.write(f"**ENTRY:** {st.session_state.ep} | **SL:** {st.session_state.sl} | **TARGET:** {st.session_state.tg}")

else:
    st.info("📡 जार्विस बड़े खिलाड़ियों के डेटा और न्यूज़ इम्पैक्ट को स्कैन कर रहा है... कृपया 5 सेकंड रुकें।")

# --- 🛡️ MASTER RESET ---
st.write("---")
if st.button("🔄 CLEAR ALL & NEW SCAN"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()
