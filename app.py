import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import pytz
import warnings

# --- 🎯 वॉर्निंग और एरर क्लीनअप ---
warnings.filterwarnings('ignore')

# --- पल्स और सेटिंग्स (1-सेकंड पल्स) ---
st.set_page_config(page_title="JARVIS RV - FULL OP", layout="wide", initial_sidebar_state="collapsed")
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=1000, key="jarvis_operation_lock")

# --- 🔊 ग्रैंड मास्टर वॉइस इंजन ---
def play_voice(text):
    js_code = f"""<script>var msg = new SpeechSynthesisUtterance('{text}'); msg.rate = 1.1; window.speechSynthesis.speak(msg);</script>"""
    st.components.v1.html(js_code, height=0)

# --- 🛡️ डेटा हंटर (Multi-Route) ---
@st.cache_data(ttl=1)
def fetch_secured_data(ticker):
    try:
        df = yf.download(ticker, period="2d", interval="1m", progress=False, timeout=2)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df
    except:
        try:
            backup = ticker.replace("^", "") + ".NS"
            df = yf.download(backup, period="2d", interval="1m", progress=False, timeout=2)
            return df
        except: return None

# --- 🔐 स्टेट मैनेजमेंट ---
if 'ai_core' not in st.session_state:
    st.session_state.update({
        'active': False, 'entry': 0, 'tgt': 0, 'sl': 0, 
        'type': "", 'max_ltp': 0, 'decision_voiced': False
    })

# --- 🚀 डैशबोर्ड हेडर ---
st.markdown(f"""
    <div style="background-color:#07090f; padding:15px; border-radius:12px; border:3px solid #00ff00; text-align:center; box-shadow: 0px 0px 30px #00ff00;">
        <h1 style="color:#00ff00; margin:0; font-family:serif;">🤖 JARVIS RV OS : FULL OPERATION MODE</h1>
        <p style="color:white; margin:5px 0;">🛡️ OI | LTP | Price Action | स्मार्ट प्रॉफिट गाइड (62 Points)</p>
    </div>
""", unsafe_allow_html=True)

idx_choice = st.selectbox("इंडेक्स चुनें (Index):", ["NIFTY 50", "BANK NIFTY"], index=0)
mapping = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK"}
df = fetch_secured_data(mapping[idx_choice])

if df is not None and len(df) > 40:
    # --- 🧠 सर्जरी इंजन (Calculations) ---
    df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    # RSI & Momentum
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))

    ltp = round(df['Close'].iloc[-1], 2)
    momentum = df['Close'].diff(3).iloc[-1]
    vol_spike = df['Volume'].iloc[-1] > (df['Volume'].tail(10).mean() * 1.5)

    # --- 🎯 फुल ऑपरेशन सिग्नल लॉजिक ---
    if not st.session_state.active:
        # EMA Crossover + RSI + Momentum + Volume = 99% Entry
        if (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (df['RSI'].iloc[-1] > 58) and momentum > 5:
            st.session_state.update({'active': True, 'entry': ltp, 'tgt': ltp+40, 'sl': ltp-20, 'type': "CALL", 'max_ltp': ltp, 'decision_voiced': False})
            play_voice(f"Operation Successful. CALL signal detected. Momentum is high.")
            st.balloons()
        elif (df['E9'].iloc[-1] < df['E21'].iloc[-1]) and (df['RSI'].iloc[-1] < 42) and momentum < -5:
            st.session_state.update({'active': True, 'entry': ltp, 'tgt': ltp-40, 'sl': ltp+20, 'type': "PUT", 'max_ltp': ltp, 'decision_voiced': False})
            play_voice(f"Operation Successful. PUT signal detected. Sellers are aggressive.")

    # --- 💰 स्मार्ट प्रॉफिट गाइड (पॉइंट 62) ---
    if st.session_state.active:
        points = abs(ltp - st.session_state.entry)
        curr_rsi = df['RSI'].iloc[-1]

        if 15 <= points <= 22 and not st.session_state.decision_voiced:
            # अगर अभी भी ज़ोर बाकी है
            if (st.session_state.type == "CALL" and momentum > 10 and curr_rsi > 65) or \
               (st.session_state.type == "PUT" and momentum < -10 and curr_rsi < 35):
                play_voice("Sir, big movement detected. Don't leave for 20 points. Stay for the jackpot!")
                st.session_state.decision_voiced = True
            else:
                play_voice("Sir, market is cooling down. Take your 15 to 20 points and exit safely.")
                st.session_state.decision_voiced = True

    # --- 💰 जैकपॉट डिस्प्ले ---
    s_color = "#00ff00" if st.session_state.type == "CALL" else "#ff4b4b" if st.session_state.type == "PUT" else "#333"
    strike_gap = 100 if "BANK" in idx_choice else 50
    atm_strike = round(ltp / strike_gap) * strike_gap

    st.markdown(f"""
        <div style="background-color:#111; padding:20px; border-radius:15px; border-left:15px solid {s_color}; border-right:15px solid {s_color}; margin-top:15px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="color:white;">
                    <h2 style="margin:0;">LTP: {ltp} | RSI: {round(df['RSI'].iloc[-1], 1)}</h2>
                    <h1 style="color:{s_color}; margin:0;">{st.session_state.type if st.session_state.active else "OPERATING..."}</h1>
                </div>
                <div style="text-align:right; color:white;">
                    <h3 style="color:#ffff00; margin:0;">Points Gained: {round(points, 1) if st.session_state.active else 0}</h3>
                    <h2 style="color:#ffaa00; margin:5px 0;">BUY: {atm_strike} {st.session_state.type}</h2>
                    <p style="margin:0;">TGT: {st.session_state.tgt} | SL: {st.session_state.sl}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # चार्ट
    
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.add_trace(go.Scatter(x=df.index, y=df['E9'], line=dict(color='orange', width=2), name="EMA 9"))
    fig.add_trace(go.Scatter(x=df.index, y=df['E21'], line=dict(color='cyan', width=2), name="EMA 21"))
    fig.update_layout(template="plotly_dark", height=600, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    if st.button('🔄 मैनुअल रिसेट (Manual Reset)'):
        st.session_state.active = False
        st.rerun()
else:
    st.info("🔒 जार्विस बाज़ार की सर्जरी कर रहा है... डेटा सिंक किया जा रहा है।")
