import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import pytz
import warnings

# --- 🎯 पॉइंट 56: एरर फिक्स (बदला हुआ तरीका) ---
warnings.filterwarnings('ignore')

# --- पल्स और सेटिंग्स ---
st.set_page_config(page_title="JARVIS RV - FINAL FIXED", layout="wide", initial_sidebar_state="collapsed")
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=1000, key="jarvis_final_fixed")

# --- 🔊 वॉइस इंजन ---
def play_voice(text):
    js_code = f"""<script>var msg = new SpeechSynthesisUtterance('{text}'); msg.rate = 1.1; window.speechSynthesis.speak(msg);</script>"""
    st.components.v1.html(js_code, height=0)

# --- 🛡️ डेटा बैकअप लॉजिक ---
@st.cache_data(ttl=1)
def fetch_secured_data(ticker):
    try:
        df = yf.download(ticker, period="2d", interval="1m", progress=False, timeout=2)
        if not df.empty: return df
    except:
        try:
            backup = ticker.replace("^", "") + ".NS"
            df = yf.download(backup, period="2d", interval="1m", progress=False, timeout=2)
            return df
        except: return None

# --- 🔐 स्टेट मैनेजमेंट ---
if 'ai_status' not in st.session_state:
    st.session_state.update({'active': False, 'entry': 0, 'tgt': 0, 'sl': 0, 'type': "", 'max_p': 0})

# --- 🚀 डैशबोर्ड हेडर ---
st.markdown(f"""
    <div style="background-color:#07090f; padding:15px; border-radius:12px; border:3px solid #00d4ff; text-align:center;">
        <h1 style="color:#00d4ff; margin:0;">🤖 JARVIS RV OS : V37 STABLE</h1>
        <p style="color:white; margin:5px 0;">🛡️ एरर फिक्स एक्टिव | डेटा बैकअप सुरक्षित</p>
    </div>
""", unsafe_allow_html=True)

idx_choice = st.selectbox("इंडेक्स चुनें:", ["NIFTY 50", "BANK NIFTY"], index=0)
mapping = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK"}
df = fetch_secured_data(mapping[idx_choice])

if df is not None and len(df) > 30:
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    
    # कैलकुलेशन
    df['E9'] = df['Close'].ewm(span=9).mean()
    df['E21'] = df['Close'].ewm(span=21).mean()
    ltp = round(df['Close'].iloc[-1], 2)

    # सिंपल जैकपॉट कार्ड
    st.markdown(f"""
        <div style="background-color:#111; padding:20px; border-radius:15px; border-top:5px solid #00ff00;">
            <h2 style="color:white; margin:0;">{idx_choice}: {ltp}</h2>
            <h1 style="color:#00ff00;">READY FOR SIGNAL</h1>
        </div>
    """, unsafe_allow_html=True)

    # चार्ट
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("⚠️ डेटा लोड नहीं हो रहा। कृपया इंटरनेट या बैकअप चेक करें।")
