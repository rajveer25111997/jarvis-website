import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz

# --- 🎯 सेटिंग्स और ऑटो-रिफ्रेश (पॉइंट 1-47) ---
st.set_page_config(page_title="JARVIS RV FINAL MASTER", layout="wide", initial_sidebar_state="collapsed")
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=1000, key="jarvis_ultimate_pulse") # 1-सेकंड हार्टबीट

# --- 🔊 वॉइस इंजन (पॉइंट 47) ---
def play_voice(text):
    components_html = f"""<script>var msg = new SpeechSynthesisUtterance('{text}'); window.speechSynthesis.speak(msg);</script>"""
    st.components.v1.html(components_html, height=0)

def get_ist():
    return datetime.now(pytz.timezone('Asia/Kolkata'))

@st.cache_data(ttl=1)
def fetch_secured_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False, timeout=2)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df
    except: return None

# --- 🔐 डेटा लॉक मैकेनिज्म (Target & SL Stability) ---
if 'entry_p' not in st.session_state:
    st.session_state.entry_p = 0
    st.session_state.l_tgt = 0
    st.session_state.l_sl = 0
    st.session_state.trade_on = False
    st.session_state.last_sig = ""

# --- 🚀 डैशबोर्ड हेडर ---
ticker = "^NSEI" 
df = fetch_secured_data(ticker)
ist_now = get_ist()

st.markdown(f"""
    <div style="background-color:#07090f; padding:15px; border-radius:12px; border:2px solid #00d4ff; text-align:center; box-shadow: 0px 0px 20px #00d4ff;">
        <h1 style="color:#00d4ff; margin:0; font-family:serif;">🤖 JARVIS RV OS : THE FINAL FORTRESS</h1>
        <p style="color:white; margin:5px 0;"><b>IST: {ist_now.strftime('%I:%M:%S %p')}</b> | 🛡️ 47 पॉइंट्स पूरी तरह लॉक हैं</p>
    </div>
""", unsafe_allow_html=True)

if df is not None and len(df) > 20:
    # एनालिसिस इंजन (जावेद 9/21)
    df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    curr, prev = df.iloc[-1], df.iloc[-2]
    ltp = round(curr['Close'], 2)
    diff = curr['E9'] - curr['E21']
    
    # --- 🎯 सिग्नल शुद्धिकरण और वॉइस अलर्ट ---
    sig, s_color = "WAITING", "#333"
    
    # BUY एंट्री
    if diff > 0.6 and prev['E9'] <= prev['E21'] and not st.session_state.trade_on:
        st.session_state.entry_p = ltp
        st.session_state.l_tgt = round(ltp + 50, 2)
        st.session_state.l_sl = round(ltp - 25, 2)
        st.session_state.trade_on = True
        play_voice("Nifty Buy Signal. Target Locked.")
        st.balloons()

    # SELL एंट्री
    elif diff < -0.6 and prev['E9'] >= prev['E21'] and not st.session_state.trade_on:
        st.session_state.entry_p = ltp
        st.session_state.l_tgt = round(ltp - 50, 2)
        st.session_state.l_sl = round(ltp + 25, 2)
        st.session_state.trade_on = True
        play_voice("Nifty Sell Signal. Target Locked.")

    # ट्रेड मॉनिटरिंग
    if st.session_state.trade_on:
        sig = "HOLD POSITION"
        s_color = "#00d4ff"
        # एग्जिट चेक
        if (ltp >= st.session_state.l_tgt and st.session_state.l_tgt > st.session_state.entry_p) or \
           (ltp <= st.session_state.l_tgt and st.session_state.l_tgt < st.session_state.entry_p):
            sig = "🎯 TARGET HIT - EXIT!"
            s_color = "#ffff00"
            play_voice("Target Reached. Profit Book Now.")
            st.session_state.trade_on = False

    # जैकपॉट कार्ड
    atm_s = round(ltp / 50) * 50
    st.markdown(f"""
        <div style="background-color:#11141d; padding:20px; border-radius:15px; border-left:12px solid {s_color}; margin-top:15px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="color:white;">
                    <h2 style="margin:0;">NIFTY: {ltp}</h2>
                    <h1 style="color:{s_color}; margin:0;">{sig}</h1>
                </div>
                <div style="text-align:right; color:white;">
                    <h3 style="color:#00ff00; margin:0;">TGT: {st.session_state.l_tgt if st.session_state.trade_on else '---'}</h3>
                    <h3 style="color:#ff4b4b; margin:0;">SL: {st.session_state.l_sl if st.session_state.trade_on else '---'}</h3>
                    <h2 style="color:#ffaa00; margin:5px 0;">STRIKE: {atm_s} {'CE' if sig != 'SELL' else 'PE'}</h2>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # स्टेबल चार्ट
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.add_trace(go.Scatter(x=df.index, y=df['E9'], line=dict(color='orange', width=2), name="EMA 9"))
    fig.add_trace(go.Scatter(x=df.index, y=df['E21'], line=dict(color='cyan', width=2), name="EMA 21"))
    
    if st.session_state.trade_on:
        fig.add_hline(y=st.session_state.l_tgt, line_dash="dash", line_color="green", annotation_text="LOCKED TGT")
        fig.add_hline(y=st.session_state.l_sl, line_dash="dash", line_color="red", annotation_text="LOCKED SL")
    
    fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # कंट्रोल पैनल
    if st.button('Reset System / Manual Exit'):
        st.session_state.trade_on = False
        st.rerun()

else:
    st.warning("🔒 जार्विस मास्टर सिस्टम सक्रिय हो रहा है... डेटा सिंक किया जा रहा है।")

st.caption("Jarvis RV OS v22.0 | Final Master | Voice & Lock Enabled | No-Blink")
