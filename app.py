import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz
import base64

# --- 🎯 पॉइंट 43: इमरजेंसी साउंड इंजन ---
def play_sound(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

# इमरजेंसी साउंड के लिए ऑनलाइन लिंक (Siren Sound)
ALARM_URL = "https://www.soundjay.com/buttons/beep-01a.mp3" # आप इसे अपनी किसी भी लोकल MP3 फाइल से बदल सकते हैं

st.set_page_config(page_title="JARVIS RV ULTIMATE", layout="wide")

@st.cache_data(ttl=2) 
def fetch_hunter(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df
    except: return None

# --- डैशबोर्ड ---
ticker = "^NSEI" 
df = fetch_hunter(ticker)

if df is not None and len(df) > 20:
    df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    curr = df.iloc[-1]
    prev = df.iloc[-2]
    ltp = round(curr['Close'], 2)
    
    # स्ट्राइक प्राइस और SL/TGT (पॉइंट 42)
    atm_strike = round(ltp / 50) * 50
    sl_val = round(ltp - 25, 2)
    tgt_val = round(ltp + 50, 2)
    
    # --- सिग्नल और साउंड लॉजिक ---
    sig = "WAIT"
    if curr['E9'] > curr['E21'] and prev['E9'] <= prev['E21']:
        sig = "BUY"
        # साउंड बजाओ
        st.markdown(f'<audio autoplay><source src="{ALARM_URL}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        st.balloons()
    elif curr['E9'] < curr['E21'] and prev['E9'] >= prev['E21']:
        sig = "SELL"
        st.markdown(f'<audio autoplay><source src="{ALARM_URL}" type="audio/mp3"></audio>', unsafe_allow_html=True)

    # टॉप डिस्प्ले
    st.markdown(f"""
        <div style="background-color:#1e2130; padding:20px; border-radius:15px; border-left:10px solid {'#00ff00' if sig=='BUY' else '#ff4b4b' if sig=='SELL' else '#333'};">
            <h2 style="color:white; margin:0;">💰 LIVE NIFTY: {ltp} | SIGNAL: {sig}</h2>
            <p style="color:#00ff00; font-size:18px; margin:5px 0;">🎯 TARGET: {tgt_val} | 🛡️ SL: {sl_val}</p>
            <p style="color:#ffaa00; font-size:18px;">💎 OPTION: NIFTY {atm_strike} {'CE' if sig != 'SELL' else 'PE'}</p>
        </div>
    """, unsafe_allow_html=True)

    col_main, col_side = st.columns([3, 1])
    
    with col_main:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.add_hline(y=tgt_val, line_dash="dash", line_color="green", annotation_text="TGT")
        fig.add_hline(y=sl_val, line_dash="dash", line_color="red", annotation_text="SL")
        fig.add_trace(go.Scatter(x=df.index, y=df['E9'], line=dict(color='orange', width=1.5), name="EMA 9"))
        fig.add_trace(go.Scatter(x=df.index, y=df['E21'], line=dict(color='cyan', width=1.5), name="EMA 21"))
        fig.update_layout(template="plotly_dark", height=600, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col_side:
        st.subheader("🛡️ कंट्रोल")
        st.write(f"स्ट्राइक: **{atm_strike}**")
        if st.button('🔄 Refresh Data'):
            st.rerun()

st.caption("Jarvis RV OS v13.0 | 43 Points Emergency Alert Edition")
