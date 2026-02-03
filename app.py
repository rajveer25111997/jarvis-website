import streamlit as st
import pandas as pd
import requests
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME SETTINGS ---
st.set_page_config(page_title="Jarvis NSE Master", layout="wide")
st_autorefresh(interval=3000, key="jarvis_nse_only")

# --- 🔊 2. MASTER VOICE ENGINE ---
def jarvis_speak(text):
    if text:
        js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang='hi-IN'; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 🧠 3. PERMANENT BRAIN (Stock Memory) ---
if "init" not in st.session_state:
    st.session_state.update({
        "locked": False, "signal": "SCANNING", 
        "ep": 0.0, "sl": 0.0, "tg": 0.0,
        "why": "बड़े खिलाड़ियों और इंडेक्स की सभी कंपनियों को स्कैन कर रहा हूँ...",
        "capital_inr": 10000.0
    })

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🛡️ JARVIS NSE COMMANDER v116.0</h1>", unsafe_allow_html=True)

if st.button("🔊 ACTIVATE JARVIS SYSTEM"):
    jarvis_speak("नमस्ते राजवीर सर, स्टॉक मार्केट मास्टर सिस्टम अब लाइव है। क्रिप्टो को हटा दिया गया है।")

# --- 📈 NSE DATA ENGINE (High-Speed Backup Logic) ---
def get_nse_data():
    try:
        # Direct Yahoo JSON Feed for Nifty 50
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

# --- ⚙️ STOCK MARKET STRATEGY (The Brain) ---
if not df.empty and len(df) > 20:
    # Javed/Karishma Indicators
    df['E9'] = ta.ema(df['Close'], length=9)
    df['E21'] = ta.ema(df['Close'], length=21)
    df['E200'] = ta.ema(df['Close'], length=200)
    ltp = round(df['Close'].iloc[-1], 2)
    
    # Operator Eye (Volume Spike Check)
    vol_now = df['Volume'].iloc[-1]
    avg_vol = df['Volume'].tail(15).mean()

    if not st.session_state.locked:
        # Strategy Combine: 9/21 Crossover + 200 EMA + Volume Confirmation
        is_call = df['E9'].iloc[-1] > df['E21'].iloc[-1] and ltp > df['E200'].iloc[-1]
        is_put = df['E9'].iloc[-1] < df['E21'].iloc[-1] and ltp < df['E200'].iloc[-1]
        big_player = vol_now > (avg_vol * 1.3) # Operator Entry Signal

        if is_call and big_player:
            st.session_state.update({
                "signal": "CALL (BUY)", "ep": ltp, "sl": ltp-50, "tg": ltp+250, "locked": True,
                "why": "बड़े खिलाड़ियों ने भारी खरीदारी शुरू की है। भाव 9/21 और 200 EMA के ऊपर मजबूत बुलिश है।"
            })
            jarvis_speak("राजवीर सर, ऑपरेटर्स की खरीदारी मिली है। एन एस ई कॉल लॉक्ड।")
        elif is_put and big_player:
            st.session_state.update({
                "signal": "PUT (SELL)", "ep": ltp, "sl": ltp+50, "tg": ltp-250, "locked": True,
                "why": "बाज़ार में बड़ी कंपनियों की बिकवाली है। ऑपरेटर्स मार्केट को नीचे ले जा रहे हैं।"
            })
            jarvis_speak("राजवीर सर, ऑपरेटर्स माल बेच रहे हैं। एन एस ई पुट लॉक्ड।")

    # --- 📊 DASHBOARD DISPLAY ---
    c1, c2, c3 = st.columns(3)
    c1.metric("NIFTY 50 LIVE", f"₹{ltp}")
    c2.success(f"📌 {st.session_state.signal}")
    
    # Capital Management (INR based)
    qty = round(st.session_state.capital_inr / (ltp * 0.1), 1) # Estimated Lot size/margin
    c3.warning(f"💰 Qty: {qty} | Cap: ₹10k")

    st.info(f"🧠 **Jarvis Analysis (Reason):** {st.session_state.why}")

    # Candlestick View
    fig = go.Figure(data=[go.Scatter(x=df.index, y=df['Close'], name='Price', line=dict(color='#00FF00', width=2))])
    fig.add_trace(go.Scatter(x=df.index, y=df['E9'], name='EMA 9', line=dict(color='yellow')))
    fig.add_trace(go.Scatter(x=df.index, y=df['E21'], name='EMA 21', line=dict(color='cyan')))
    
    fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.write(f"**LOCKED ENTRY:** {st.session_state.ep} | **STOP LOSS:** {st.session_state.sl} | **TARGET:** {st.session_state.tg}")

else:
    st.info("📡 जार्विस स्टॉक मार्केट और बड़े खिलाड़ियों की चाल को स्कैन कर रहा है... कृपया रुकें।")

# --- 🛡️ MASTER SYSTEM RESET ---
st.write("---")
if st.button("🔄 CLEAR & NEW NSE SCAN"):
    for key in ["locked", "signal", "ep", "sl", "tg", "why"]:
        if key in st.session_state: del st.session_state[key]
    st.rerun()
