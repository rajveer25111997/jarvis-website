import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
import warnings
from datetime import datetime

# --- 🎯 1. CORE SETUP ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="JARVIS SNIPER V4", layout="wide", initial_sidebar_state="collapsed")

# --- 🧠 2. DATA ENGINE ---
def get_data_safe(ticker):
    try:
        df = yf.download(ticker, period="2d", interval="1m", progress=False, auto_adjust=True)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df
    except: return None

# --- 🔍 3. STATIC UI & STATE ---
st.markdown("<h1 style='text-align:center; color:#00ff00; margin:0;'>🤖 JARVIS SNIPER OS</h1>", unsafe_allow_html=True)

# Session States (Trade Memory)
if "daily_trades" not in st.session_state: st.session_state.daily_trades = 0
if "last_sig" not in st.session_state: st.session_state.last_sig = ""
if "entry" not in st.session_state: st.session_state.entry = 0.0

# --- 🏗️ 4. SNIPER EXECUTION AREA ---
live_dashboard = st.empty()

@st.fragment(run_every=1)
def jarvis_sniper_engine():
    ticker, gap = "^NSEI", 50
    df = get_data_safe(ticker)
    
    if df is not None:
        ltp = round(float(df['Close'].iloc[-1]), 2)
        
        # Strategy Logic (Javed 9/21 + 200 EMA)
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        df['E200'] = df['Close'].ewm(span=200, adjust=False).mean()
        
        is_buy = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (ltp > df['E200'].iloc[-1])
        is_sell = (df['E9'].iloc[-1] < df['E21'].iloc[-1]) and (ltp < df['E200'].iloc[-1])
        
        atm = round(ltp / gap) * gap
        prem = round((ltp * 0.0078) + (abs(ltp - atm) * 0.55), 2)

        # 🛡️ SNIPER LOCK LOGIC (Limit to 4 Trades)
        if st.session_state.daily_trades >= 4:
            sig, col = "🏁 QUOTA COMPLETED", "#555555"
            status_msg = "Rajveer Sir, today's 4 trades are done. Let's protect the capital!"
        else:
            if is_buy: sig, col = "💎 MASTER BUY", "#00ff00"
            elif is_sell: sig, col = "🚨 MASTER SELL", "#ff4b4b"
            else: sig, col = "⌛ SCANNING...", "#555555"
            status_msg = f"Sniper Mode Active: {st.session_state.daily_trades}/4 used"

        # Voice Alerts (Only if under limit)
        if "MASTER" in sig and st.session_state.last_sig != sig and st.session_state.daily_trades < 4:
            st.session_state.daily_trades += 1
            st.session_state.last_sig = sig
            st.session_state.entry = prem
            voice = f"<script>window.speechSynthesis.speak(new SpeechSynthesisUtterance('Rajveer Sir, Trade {st.session_state.daily_trades} detected at {prem}'));</script>"
            st.components.v1.html(voice, height=0)

        with live_dashboard.container():
            # Header Stats
            st.markdown(f"<p style='text-align:center; color:white;'>{status_msg} | {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
            
            c1, c2 = st.columns([2, 1])
            with c1:
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True, key=f"ch_{time.time()}")
            
            with c2:
                st.markdown(f"""<div style='background:#111; padding:20px; border-radius:15px; border:1px solid #333; text-align:center; height:400px; display:flex; flex-direction:column; justify-content:center;'>
                    <h2 style='color:#00ff00;'>LTP: {ltp}</h2>
                    <h4 style='color:white;'>ATM: {atm}</h4>
                    <h1 style='color:{col}; font-size:60px; margin:10px 0;'>₹{prem}</h1>
                    <p style='color:gray;'>QUOTA: {st.session_state.daily_trades}/4</p></div>""", unsafe_allow_html=True)
            
            # Big Signal UI
            st.markdown(f"""<div style='background:#07090f; padding:25px; border-radius:20px; border:5px solid {col}; text-align:center; box-shadow: 0px 0px 25px {col};'>
                <h1 style='color:{col}; margin:0; font-size:45px;'>{sig}</h1>
                <div style='display:flex; justify-content:space-around; margin-top:15px;'>
                    <div><p style='color:gray;'>ENTRY</p><h2 style='color:white;'>₹{st.session_state.entry if st.session_state.entry>0 else '---'}</h2></div>
                    <div><p style='color:#00ff00;'>TGT (+20)</p><h2 style='color:#00ff00;'>₹{round(st.session_state.entry+20, 2) if st.session_state.entry>0 else '---'}</h2></div>
                    <div><p style='color:#ff4b4b;'>KARISHMA SL</p><h2 style='color:#ff4b4b;'>₹{round(st.session_state.entry-10, 2) if st.session_state.entry>0 else '---'}</h2></div>
                </div></div>""", unsafe_allow_html=True)

# 🚀 Execute
jarvis_sniper_engine()
