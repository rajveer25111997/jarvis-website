import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz

# --- 🎯 सेटिंग्स और ऑटो-रिफ्रेश (पॉइंट 1-10) ---
st.set_page_config(page_title="JARVIS RV FINAL", layout="wide", initial_sidebar_state="collapsed")
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=1000, key="jarvis_final_pulse") # 1-सेकंड पल्स

def get_ist():
    return datetime.now(pytz.timezone('Asia/Kolkata'))

@st.cache_data(ttl=1)
def fetch_secured_data(ticker):
    try:
        # पॉइंट 38: सुपर फास्ट डेटा हंटर (timeout के साथ ताकि अटके नहीं)
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
    <div style="background-color:#07090f; padding:15px; border-radius:12px; border:2px solid #00d4ff; text-align:center; box-shadow: 0px 0px 20px #00d4ff;">
        <h1 style="color:#00d4ff; margin:0; font-family:serif;">🤖 JARVIS RV OS : FINAL MASTER</h1>
        <p style="color:white; margin:5px 0;"><b>IST: {ist_now.strftime('%I:%M:%S %p')}</b> | 🛡️ 45 पॉइंट्स पूरी तरह लॉक हैं</p>
    </div>
""", unsafe_allow_html=True)

if df is not None and len(df) > 20:
    # --- 🧠 जार्विस एनालिसिस इंजन (जावेद 9/21 + शुद्धिकरण) ---
    df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    curr, prev = df.iloc[-1], df.iloc[-2]
    ltp = round(curr['Close'], 2)
    diff = curr['E9'] - curr['E21']
    
    # --- 🎯 बराबर सिग्नल लॉजिक (Precision Mode) ---
    sig, s_color = "WAIT", "#333"
    # अगर अंतर 0.5 से ज़्यादा है तभी सिग्नल को 'Confirmed' मानो (फेक सिग्नल रोकने के लिए)
    if diff > 0.5 and prev['E9'] <= prev['E21']:
        sig, s_color = "BUY", "#00ff00"
    elif diff < -0.5 and prev['E9'] >= prev['E21']:
        sig, s_color = "SELL", "#ff4b4b"

    # इमरजेंसी सायरन (Alert Sound)
    if sig != "WAIT":
        st.markdown(f'<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mp3"></audio>', unsafe_allow_html=True)
        if sig == "BUY": st.balloons()

    # स्ट्राइक प्राइस और SL/TGT (पॉइंट 42)
    atm_strike = round(ltp / 50) * 50
    sl_val, tgt_val = round(ltp - 25, 2), round(ltp + 55, 2)

    # --- 💰 जैकपॉट कार्ड डिस्प्ले ---
    st.markdown(f"""
        <div style="background-color:#11141d; padding:20px; border-radius:15px; border-left:12px solid {s_color}; margin-top:15px; border-right:12px solid {s_color};">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="color:white;">
                    <h2 style="margin:0;">NIFTY 50: <span style="color:#00d4ff;">{ltp}</span></h2>
                    <h1 style="color:{s_color}; margin:0;">{sig} CONFIRMED</h1>
                </div>
                <div style="text-align:right; color:white;">
                    <h3 style="color:#00ff00; margin:0;">🎯 TARGET: {tgt_val}</h3>
                    <h3 style="color:#ff4b4b; margin:0;">🛡️ STOP LOSS: {sl_val}</h3>
                    <h2 style="color:#ffaa00; margin:5px 0;">💎 {atm_strike} {'CE' if sig != 'SELL' else 'PE'} BUY</h2>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- 📊 स्टेबल चार्ट (No Blinking) ---
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.add_trace(go.Scatter(x=df.index, y=df['E9'], line=dict(color='orange', width=2), name="EMA 9 (जावेद)"))
    fig.add_trace(go.Scatter(x=df.index, y=df['E21'], line=dict(color='cyan', width=2), name="EMA 21 (जावेद)"))
    
    # चार्ट पर SL/TGT की लाइनें
    fig.add_hline(y=tgt_val, line_dash="dash", line_color="green", annotation_text="TGT")
    fig.add_hline(y=sl_val, line_dash="dash", line_color="red", annotation_text="SL")
    
    fig.update_layout(template="plotly_dark", height=550, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # --- 🛡️ रिस्क और व्हेल रडार ---
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("रिस्क/रिवॉर्ड", "1:2.2")
    with c2: 
        vol_active = df['Volume'].iloc[-1] > df['Volume'].tail(10).mean()
        st.metric("Whale Radar", "सक्रिय ✅" if vol_active else "शांत ⏳")
    with c3: st.metric("Portfolio", "RVNL: HOLD")

else:
    st.info("🔒 जार्विस मास्टर सिस्टम लोड हो रहा है... डेटा सिंक किया जा रहा है।")

st.markdown("<p style='text-align:center; color:#444; margin-top:20px;'>Jarvis RV Final Master OS v19.0 | 45 Points Secured | No-Blink Mode</p>", unsafe_allow_html=True)
