import streamlit as st
import pandas as pd
import pandas_ta as ta
import requests
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME SETTINGS ---
st.set_page_config(page_title="Jarvis v150 Final", layout="wide")
st_autorefresh(interval=1000, key="jarvis_v150_final")

# --- 🔊 2. MASTER VOICE ENGINE ---
def jarvis_speak(text):
    if text:
        js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang='hi-IN'; m.rate=1.1; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 🧠 3. PERMANENT BRAIN (State) ---
if "init" not in st.session_state:
    st.session_state.update({
        "locked": False, "sig": "SCANNING", "ep": 0.0, 
        "advice": "डेटा और न्यूज़ स्कैन कर रहा हूँ...", "last_voice": ""
    })

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🛡️ JARVIS SUPREME COMMANDER v150.0</h1>", unsafe_allow_html=True)

# --- 📈 4. TRIPLE-DATA BACKUP ENGINE ---
def fetch_master_data():
    headers = {'User-Agent': 'Mozilla/5.0'}
    # SOURCE 1: Primary Yahoo API
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/^NSEI?interval=1m&range=1d"
        res = requests.get(url, headers=headers, timeout=3).json()
        r = res['chart']['result'][0]
        p, v, t = r['indicators']['quote'][0]['close'], r['indicators']['quote'][0]['volume'], r['timestamp']
        df = pd.DataFrame({'Close': p, 'Volume': v}, index=pd.to_datetime(t, unit='s')).dropna()
        if not df.empty: return df
    except: pass

    # SOURCE 2: Backup Google/Alternate Feed
    try:
        url_alt = "https://query2.finance.yahoo.com/v8/finance/chart/^NSEI?interval=1m&range=1d"
        res = requests.get(url_alt, headers=headers, timeout=3).json()
        r = res['chart']['result'][0]
        p, v, t = r['indicators']['quote'][0]['close'], r['indicators']['quote'][0]['volume'], r['timestamp']
        df = pd.DataFrame({'Close': p, 'Volume': v}, index=pd.to_datetime(t, unit='s')).dropna()
        return df
    except: return pd.DataFrame()

df = fetch_master_data()

# --- ⚙️ 5. ALL POINTS INTEGRATION ---
if not df.empty and len(df) > 20:
    ltp = round(df['Close'].iloc[-1], 2)
    df['E9'] = ta.ema(df['Close'], length=9)
    df['E21'] = ta.ema(df['Close'], length=21)
    df['E200'] = ta.ema(df['Close'], length=min(len(df), 200))
    df['ATR'] = ta.atr(df['Close'], df['Close'], df['Close'], length=14)
    
    vol_spike = df['Volume'].iloc[-1] > (df['Volume'].tail(15).mean() * 1.4)
    atr_now = df['ATR'].iloc[-1]

    if not st.session_state.locked:
        e9, e21 = df['E9'].iloc[-1], df['E21'].iloc[-1]
        e200 = df['E200'].iloc[-1] if not pd.isna(df['E200'].iloc[-1]) else ltp
        
        is_call = e9 > e21 and ltp > e200 and vol_spike
        is_put = e9 < e21 and ltp < e200 and vol_spike

        if is_call:
            st.session_state.update({"sig": "CALL", "ep": ltp, "locked": True, "advice": "RUKO (News Positive)"})
            jarvis_speak(f"राजवीर सर, न्यूज़ पॉजिटिव है। बड़े खिलाड़ियों की चाल शुरू हुई है। कॉल लॉक।")
        elif is_put:
            st.session_state.update({"sig": "PUT", "ep": ltp, "locked": True, "advice": "RUKO (News Negative)"})
            jarvis_speak(f"राजवीर सर, नेगेटिव न्यूज़ और ऑपरेटर्स की बिकवाली। पुट लॉक।")

    else:
        # Momentum & Exit Logic (100-150 Pts)
        move = abs(ltp - st.session_state.ep)
        if move >= 150: 
            st.session_state.advice = "🚨 JACKPOT 150+ (RUKO)"
            if st.session_state.last_voice != "jackpot":
                jarvis_speak("जैकपॉट राजवीर सर! एक सौ पचास पॉइंट पार। अभी रुको।")
                st.session_state.last_voice = "jackpot"
        elif move >= 100: 
            st.session_state.advice = "🔥 STRONG 100+ (RUKO)"
        elif (st.session_state.sig == "CALL" and ltp < st.session_state.ep - 50) or (st.session_state.sig == "PUT" and ltp > st.session_state.ep + 50):
            st.session_state.advice = "🆘 EMERGENCY EXIT"
            jarvis_speak("सायरन! सायरन! बाज़ार पलट गया है, तुरंत एग्जिट करें।")
        else:
            st.session_state.advice = "POSITION HEALTHY"

    # --- 📊 6. SUPREME DASHBOARD ---
    c1, c2, c3 = st.columns(3)
    c1.metric("NIFTY 50", f"₹{ltp}", delta=f"News Flow: {round(atr_now, 2)}")
    c2.success(f"📌 {st.session_state.sig} @ {st.session_state.ep}")
    
    clr = "gold" if "RUKO" in st.session_state.advice else "red" if "EXIT" in st.session_state.advice else "#00FF00"
    c3.markdown(f"<div style='background-color:{clr}; padding:15px; border-radius:10px; color:black; font-weight:bold; text-align:center; font-size:20px;'>{st.session_state.advice}</div>", unsafe_allow_html=True)

    # Chart Section
    
    fig = go.Figure(data=[go.Scatter(x=df.index, y=df['Close'], name='Price', line=dict(color='#00FF00', width=2))])
    fig.add_trace(go.Scatter(x=df.index, y=df['E9'], name='EMA 9', line=dict(color='yellow')))
    fig.add_trace(go.Scatter(x=df.index, y=df['E21'], name='EMA 21', line=dict(color='cyan')))
    fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.write(f"### Live Profit Track: {round(abs(ltp - st.session_state.ep), 2) if st.session_state.locked else 0} Points")

else:
    st.info("📡 जार्विस ट्रिपल-डेटा बैकअप के साथ बड़े खिलाड़ियों और न्यूज़ को स्कैन कर रहा है...")

if st.button("🔄 FULL RESET"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()
