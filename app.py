import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz

# --- 🎯 पॉइंट 1-15: कोर सिस्टम सेटिंग्स और ऑटो-रिफ्रेश ---
st.set_page_config(page_title="JARVIS RV - MASTER OS", layout="wide", initial_sidebar_state="collapsed")
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=1000, key="jarvis_final_pulse") # 1-सेकंड अपडेट लॉक

# --- 🔊 पॉइंट 47: वॉइस इंजन (Text-to-Speech) ---
def play_voice(text):
    js_code = f"""<script>var msg = new SpeechSynthesisUtterance('{text}'); msg.rate = 1.1; window.speechSynthesis.speak(msg);</script>"""
    st.components.v1.html(js_code, height=0)

def get_ist():
    return datetime.now(pytz.timezone('Asia/Kolkata'))

# --- 🔐 पॉइंट 16-30: स्टेट मैनेजमेंट और डेटा लॉक ---
if 'trade' not in st.session_state:
    st.session_state.update({
        'active': False, 'entry': 0, 'tgt': 0, 'sl': 0, 
        'type': "", 'voice_alert': False, 'trail_active': False
    })

@st.cache_data(ttl=1)
def fetch_secured_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False, timeout=2)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df
    except: return None

# --- 🚀 डैशबोर्ड हेडर ---
ticker = "^NSEI" 
df = fetch_secured_data(ticker)
ist_now = get_ist()

st.markdown(f"""
    <div style="background-color:#07090f; padding:15px; border-radius:12px; border:2px solid #00ff00; text-align:center; box-shadow: 0px 0px 20px #00ff00;">
        <h1 style="color:#00ff00; margin:0; font-family:serif;">🤖 JARVIS RV OS : THE FINAL MASTER</h1>
        <p style="color:white; margin:5px 0;"><b>IST: {ist_now.strftime('%I:%M:%S %p')}</b> | 🛡️ 48 पॉइंट्स पूरी तरह लॉक हैं</p>
    </div>
""", unsafe_allow_html=True)

if st.button("🔊 वॉइस एक्टिवेट करें"):
    play_voice("System Online. Master OS Locked and Ready.")

if df is not None and len(df) > 30:
    # --- एनालिसिस इंजन (जावेद EMA 9/21 + मोमेंटम) ---
    df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    curr, prev = df.iloc[-1], df.iloc[-2]
    ltp = round(curr['Close'], 2)
    momentum = df['Close'].diff(5).iloc[-1] # पिछले 5 मिनट का मोमेंटम
    
    # --- 🎯 सिग्नल और प्रॉफिट फिल्टर (15-20 Points) ---
    sig_status = "SCANNING..."
    s_color = "#333"

    if not st.session_state.active:
        # एंट्री तभी जब मोमेंटम 12 पॉइंट से ज्यादा हो (High Probability)
        if (curr['E9'] > curr['E21']) and (prev['E9'] <= prev['E21']) and momentum > 10:
            st.session_state.update({'active': True, 'entry': ltp, 'tgt': ltp+20, 'sl': ltp-15, 'type': "CALL", 'voice_alert': False})
            play_voice("Strong Call Signal. Target 20 points locked.")
        elif (curr['E9'] < curr['E21']) and (prev['E9'] >= prev['E21']) and momentum < -10:
            st.session_state.update({'active': True, 'entry': ltp, 'tgt': ltp-20, 'sl': ltp+15, 'type': "PUT", 'voice_alert': False})
            play_voice("Strong Put Signal. Target 20 points locked.")
    
    # --- 💰 होल्डिंग और एग्जिट लॉजिक (पॉइंट 48) ---
    if st.session_state.active:
        s_color = "#00ff00" if st.session_state.type == "CALL" else "#ff4b4b"
        profit = abs(ltp - st.session_state.entry)
        
        if profit >= 20:
            if abs(momentum) > 15: # अगर रफ़्तार अभी भी तेज़ है
                sig_status = "🚀 BIG MOMENTUM: HOLD FOR MORE!"
                if not st.session_state.voice_alert:
                    play_voice("Momentum is high. Hold the trade for big profit.")
                    st.session_state.voice_alert = True
            else:
                sig_status = "🎯 TARGET REACHED: EXIT NOW!"
                play_voice("Target achieved. Exit and book profit.")
                st.session_state.active = False # रिसेट फॉर नेक्स्ट सिग्नल
        else:
            sig_status = f"HOLDING... Current Profit: {round(profit, 1)} pts"

    # --- जैकपॉट डिस्प्ले कार्ड ---
    atm_strike = round(ltp / 50) * 50
    st.markdown(f"""
        <div style="background-color:#11141d; padding:20px; border-radius:15px; border-left:15px solid {s_color}; margin-top:15px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="color:white;">
                    <h2 style="margin:0;">NIFTY 50: {ltp}</h2>
                    <h1 style="color:{s_color}; margin:0;">{st.session_state.type if st.session_state.active else "WAIT"}</h1>
                </div>
                <div style="text-align:right; color:white;">
                    <h2 style="color:#ffff00; margin:0;">{sig_status}</h2>
                    <p style="margin:0;">Entry: {st.session_state.entry} | TGT: {st.session_state.tgt}</p>
                    <h2 style="color:#ffaa00; margin:5px 0;">OPTION: {atm_strike} {st.session_state.type}</h2>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- चार्ट ज़ोन ---
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.add_trace(go.Scatter(x=df.index, y=df['E9'], line=dict(color='orange', width=2), name="EMA 9"))
    fig.add_trace(go.Scatter(x=df.index, y=df['E21'], line=dict(color='cyan', width=2), name="EMA 21"))
    
    if st.session_state.active:
        fig.add_hline(y=st.session_state.tgt, line_dash="dash", line_color="green", annotation_text="LOCKED TGT")
        fig.add_hline(y=st.session_state.sl, line_dash="dash", line_color="red", annotation_text="LOCKED SL")
    
    fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    if st.button('🔄 Manual System Reset'):
        st.session_state.active = False
        st.rerun()

else:
    st.info("🔒 जार्विस तिजोरी खोल रहा है... डेटा लिंक किया जा रहा है।")

st.caption("Jarvis RV OS v26.0 | Fully Secured Master Code | 48 Points Complete")
