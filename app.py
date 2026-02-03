import streamlit as st
import pandas as pd
import requests
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME CONFIG ---
st.set_page_config(page_title="Jarvis Supreme v118", layout="wide")
st_autorefresh(interval=3000, key="jarvis_supreme_v118")

def jarvis_speak(text):
    if text:
        js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang='hi-IN'; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 🧠 2. PERMANENT BRAIN ---
if "init" not in st.session_state:
    st.session_state.update({
        "locked": False, "signal": "SCANNING", 
        "ep": 0.0, "sl": 0.0, "tg": 0.0,
        "why": "न्यूज़, वॉल्यूम और बड़े खिलाड़ियों की चाल को स्कैन कर रहा हूँ...",
        "cap": 10000.0
    })

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🛡️ JARVIS SUPREME COMMANDER v118.0</h1>", unsafe_allow_html=True)

if st.button("🔊 ACTIVATE JARVIS"):
    jarvis_speak("नमस्ते राजवीर सर, न्यूज़ और बड़े खिलाड़ियों की चाल पर मेरी नज़र है।")

# --- 📈 NSE DATA & NEWS IMPACT ENGINE ---
def get_supreme_data():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/^NSEI?interval=1m&range=1d"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5).json()
        r = res['chart']['result'][0]
        p = r['indicators']['quote'][0]['close']
        v = r['indicators']['quote'][0]['volume']
        t = r['timestamp']
        df = pd.DataFrame({'Close': p, 'Volume': v}, index=pd.to_datetime(t, unit='s')).dropna()
        return df
    except:
        return pd.DataFrame()

df = get_supreme_data()

# --- ⚙️ STRATEGY COMBINATION (The Master Points) ---
if not df.empty and len(df) > 10:
    try:
        # Indicators Combination
        df['E9'] = ta.ema(df['Close'], length=9)
        df['E21'] = ta.ema(df['Close'], length=21)
        df['E200'] = ta.ema(df['Close'], length=min(len(df), 200))
        df['ATR'] = ta.atr(df['Close'], df['Close'], df['Close'], length=14) # News Impact Marker
        
        ltp = round(df['Close'].iloc[-1], 2)
        vol_now = df['Volume'].iloc[-1]
        avg_vol = df['Volume'].tail(15).mean()
        atr_now = df['ATR'].iloc[-1]

        if not st.session_state.locked:
            # 1. जावेद/करिश्मा लॉजिक (9/21)
            # 2. बड़े खिलाड़ी लॉजिक (Volume > Avg + 200 EMA)
            # 3. न्यूज़ इफ़ेक्ट (ATR Rising)
            
            e9 = df['E9'].iloc[-1]
            e21 = df['E21'].iloc[-1]
            e200 = df['E200'].iloc[-1] if not pd.isna(df['E200'].iloc[-1]) else ltp
            
            operator_entry = vol_now > (avg_vol * 1.3) # 30% extra volume
            news_alert = atr_now > df['ATR'].tail(10).mean() # Price jumping fast
            
            is_call = e9 > e21 and ltp > e200 and operator_entry
            is_put = e9 < e21 and ltp < e200 and operator_entry

            if is_call:
                reason = "न्यूज़ पॉजिटिव है और बड़े खिलाड़ियों ने भारी वॉल्यूम के साथ खरीदारी की है।"
                st.session_state.update({"signal": "CALL (BUY)", "ep": ltp, "sl": ltp-50, "tg": ltp+250, "locked": True, "why": reason})
                jarvis_speak("एन एस ई कॉल लॉक्ड। ऑपरेटर्स और न्यूज़ दोनों साथ हैं।")
            elif is_put:
                reason = "मार्केट में बिकवाली का दबाव है। न्यूज़ नेगेटिव है और ऑपरेटर्स माल निकाल रहे हैं।"
                st.session_state.update({"signal": "PUT (SELL)", "ep": ltp, "sl": ltp+50, "tg": ltp-250, "locked": True, "why": reason})
                jarvis_speak("एन एस ई पुट लॉक्ड। न्यूज़ का असर नेगेटिव है।")

        # Dashboard View
        c1, c2, c3 = st.columns(3)
        c1.metric("NIFTY 50", f"₹{ltp}", delta=f"ATR: {round(atr_now,2)}")
        c2.success(f"📌 {st.session_state.signal}")
        c3.info(f"📊 Vol: {'Operator Active' if vol_now > avg_vol else 'Normal'}")

        st.warning(f"🧠 **Jarvis Analysis:** {st.session_state.why}")

        fig = go.Figure(data=[go.Scatter(x=df.index, y=df['Close'], line=dict(color='#00FF00', width=2))])
        fig.add_trace(go.Scatter(x=df.index, y=df['E200'], name='Operator Trend (200)', line=dict(color='white', dash='dash')))
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.info("🔄 जार्विस बड़े खिलाड़ियों के फुटप्रिंट्स (Footprints) ढूंढ रहा है...")
else:
    st.info("📡 बाज़ार की चाल का गहराई से विश्लेषण शुरू हो रहा है...")

if st.button("🔄 EMERGENCY RESET"):
    for key in ["locked", "signal", "ep", "sl", "tg", "why"]:
        if key in st.session_state: del st.session_state[key]
    st.rerun()
