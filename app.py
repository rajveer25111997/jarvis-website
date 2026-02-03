import streamlit as st
import pandas as pd
import requests
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME CONFIGURATION ---
st.set_page_config(page_title="Jarvis Ultimate v125", layout="wide")
st_autorefresh(interval=3000, key="jarvis_final_v125")

def jarvis_speak(text):
    if text:
        js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang='hi-IN'; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 🧠 2. PERMANENT BRAIN (State Management) ---
if "init" not in st.session_state:
    st.session_state.update({
        "locked": False, "signal": "SCANNING", 
        "ep": 0.0, "advice": "खोज जारी है...", 
        "why": "न्यूज़, वॉल्यूम और बड़े खिलाड़ियों के डेटा को स्कैन कर रहा हूँ...",
        "cap": 10000.0
    })

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🏛️ JARVIS ULTIMATE SUPREME v125.0</h1>", unsafe_allow_html=True)

if st.button("🔊 ACTIVATE JARVIS SYSTEM"):
    jarvis_speak("नमस्ते राजवीर सर, जार्विस का मुकम्मल सिस्टम अब लाइव है।")

# --- 📈 3. DATA ENGINE (Triple Backup) ---
def get_data():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/^NSEI?interval=1m&range=1d"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5).json()
        r = res['chart']['result'][0]
        p = r['indicators']['quote'][0]['close']
        v = r['indicators']['quote'][0]['volume']
        t = r['timestamp']
        df = pd.DataFrame({'Close': p, 'Volume': v}, index=pd.to_datetime(t, unit='s')).dropna()
        return df
    except: return pd.DataFrame()

df = get_data()

# --- ⚙️ 4. CORE STRATEGY & MOMENTUM LOGIC ---
if not df.empty and len(df) > 20:
    ltp = round(df['Close'].iloc[-1], 2)
    df['E9'] = ta.ema(df['Close'], length=9)
    df['E21'] = ta.ema(df['Close'], length=21)
    df['E200'] = ta.ema(df['Close'], length=min(len(df), 200))
    df['ATR'] = ta.atr(df['Close'], df['Close'], df['Close'], length=14)
    
    vol_now = df['Volume'].iloc[-1]
    avg_vol = df['Volume'].tail(15).mean()
    atr_val = df['ATR'].iloc[-1]

    # --- SIGNAL GENERATION ---
    if not st.session_state.locked:
        e9, e21 = df['E9'].iloc[-1], df['E21'].iloc[-1]
        e200 = df['E200'].iloc[-1] if not pd.isna(df['E200'].iloc[-1]) else ltp
        
        operator_in = vol_now > (avg_vol * 1.3) # 130% Volume = Operator
        
        is_call = e9 > e21 and ltp > e200 and operator_in
        is_put = e9 < e21 and ltp < e200 and operator_in

        if is_call:
            st.session_state.update({"signal": "CALL (BUY)", "ep": ltp, "locked": True, "why": "बड़े खिलाड़ियों की खरीदारी और 9/21 क्रॉसओवर मिला है।"})
            jarvis_speak("एन एस ई कॉल लॉक्ड। बड़ा मूवमेंट आने वाला है।")
        elif is_put:
            st.session_state.update({"signal": "PUT (SELL)", "ep": ltp, "locked": True, "why": "बड़े कंपनियों में बिकवाली है और ऑपरेटर्स माल छोड़ रहे हैं।"})
            jarvis_speak("एन एस ई पुट लॉक्ड। गिरावट की संभावना है।")
    
    # --- LIVE 100-150 POINT GUIDANCE ---
    else:
        move = abs(ltp - st.session_state.ep)
        
        if move >= 150:
            st.session_state.advice = "RUKO (JACKPOT 150+)"
            jarvis_speak("जैकपॉट! एक सौ पचास पॉइंट पार। राजवीर सर, अभी रुको।")
        elif move >= 100:
            st.session_state.advice = "RUKO (STRONG 100+)"
            jarvis_speak("एक सौ पॉइंट का मुनाफा। अभी बने रहें।")
        elif (st.session_state.signal == "CALL (BUY)" and ltp < st.session_state.ep - 40) or \
             (st.session_state.signal == "PUT (SELL)" and ltp > st.session_state.ep + 40):
            st.session_state.advice = "EXIT NOW (STOP LOSS)"
            jarvis_speak("मूवमेंट पलट गया है। एग्जिट करो।")
        else:
            st.session_state.advice = "HOLDING THE TRADE"

    # --- 📊 5. DASHBOARD DISPLAY ---
    c1, c2, c3 = st.columns(3)
    c1.metric("NIFTY 50", f"₹{ltp}", delta=f"ATR: {round(atr_val,2)}")
    c2.success(f"📌 {st.session_state.signal} @ {st.session_state.ep}")
    
    # Advice Box with dynamic colors
    status_clr = "gold" if "RUKO" in st.session_state.advice else "red" if "EXIT" in st.session_state.advice else "#00FF00"
    c3.markdown(f"<div style='background-color:{status_clr}; padding:10px; border-radius:10px; color:black; font-weight:bold; text-align:center;'>JARVIS STATUS: {st.session_state.advice}</div>", unsafe_allow_html=True)

    st.warning(f"🧠 **Jarvis Analysis:** {st.session_state.why}")
    st.write(f"### 📈 Live Profit/Loss: {round(abs(ltp - st.session_state.ep), 2) if st.session_state.locked else 0} Points")

    # Chart Section
    
    fig = go.Figure(data=[go.Scatter(x=df.index, y=df['Close'], name='Price', line=dict(color='#00FF00', width=2))])
    fig.add_trace(go.Scatter(x=df.index, y=df['E9'], name='EMA 9', line=dict(color='yellow')))
    fig.add_trace(go.Scatter(x=df.index, y=df['E21'], name='EMA 21', line=dict(color='cyan')))
    fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("📡 जार्विस बड़े खिलाड़ियों और 100-150 पॉइंट के मूव को स्कैन कर रहा है...")

# --- 🛡️ MASTER RESET ---
st.write("---")
if st.button("🔄 CLEAR & SCAN NEXT TRADE"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()
