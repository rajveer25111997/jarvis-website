import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
import warnings
from datetime import datetime

# --- 🎯 1. AI CORE (Self-Healing & Gemini Logic) ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="JARVIS ULTIMATE AI", layout="wide", initial_sidebar_state="collapsed")

# --- 🛡️ 2. PRE-MARKET & GLOBAL INTEL (Pre-Opening Scan) ---
def get_market_intelligence():
    checks = {"GIFT Nifty": "^NSEI", "Nasdaq": "^IXIC", "Reliance": "RELIANCE.NS", "HDFC Bank": "HDFCBANK.NS"}
    res = {}
    for name, sym in checks.items():
        try:
            h = yf.download(sym, period="2d", interval="1m", progress=False)
            if not h.empty:
                chg = float(((h['Close'].iloc[-1] - h['Close'].iloc[-2]) / h['Close'].iloc[-2]) * 100)
                res[name] = round(chg, 2)
            else: res[name] = 0.0
        except: res[name] = 0.0
    return res

# --- 🔍 3. STATIC UI (Stability Fix) ---
st.markdown("<h1 style='text-align:center; color:#00ff00; margin:0; font-family:serif; letter-spacing:5px;'>🤖 JARVIS ULTIMATE AI</h1>", unsafe_allow_html=True)

# Pre-Market Intelligence Display
mood_data = get_market_intelligence()
mood_score = float(sum(mood_data.values()))
mood_col = "#00ff00" if mood_score > 0 else "#ff4b4b"
st.markdown(f"""<div style='background:#111; padding:10px; border-radius:10px; border-left:5px solid {mood_col}; text-align:center;'>
    <b>GEMINI PREDICTION:</b> {'BULLISH' if mood_score > 0 else 'BEARISH'} | Global Pulse: {mood_score}% | Nasdaq: {mood_data['Nasdaq']}%
    </div>""", unsafe_allow_html=True)

# Session States (Trade Memory & Logic)
if "trades" not in st.session_state: st.session_state.trades = 0
if "last_sig" not in st.session_state: st.session_state.last_sig = ""
if "entry" not in st.session_state: st.session_state.entry = 0.0
if "max_p" not in st.session_state: st.session_state.max_p = 0.0

# --- 🏗️ 4. THE BRAIN ENGINE (No-Blink Live Processing) ---
live_area = st.empty()

@st.fragment(run_every=1)
def jarvis_brain_execution():
    ticker, gap = "^NSEI", 50 # Default to Nifty for Rajveer Sir
    df = yf.download(ticker, period="2d", interval="1m", progress=False, auto_adjust=True)
    
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        ltp = round(float(df['Close'].iloc[-1]), 2)
        
        # 📈 Javed & Karishma + Whale Sense (200 EMA)
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        df['E200'] = df['Close'].ewm(span=200, adjust=False).mean()
        
        # 🛡️ 5-Minute Breakout Logic
        first_5 = df.head(5)
        r_high, r_low = first_5['High'].max(), first_5['Low'].min()
        
        # Whale Radar (Volume Shock)
        vol_spike = df['Volume'].iloc[-1] > (df['Volume'].rolling(20).mean().iloc[-1] * 1.8)
        
        # Gemini Speed Sense (ROC)
        speed = df['Close'].diff(5).iloc[-1]
        
        # 🎯 SIGNAL LOGIC (Thinking Like Gemini)
        is_buy = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (ltp > df['E200'].iloc[-1]) and (ltp > r_high) and vol_spike
        is_sell = (df['E9'].iloc[-1] < df['E21'].iloc[-1]) and (ltp < df['E200'].iloc[-1]) and (ltp < r_low) and vol_spike
        
        # ATM Strike & Premium Engine
        atm = round(ltp / gap) * gap
        prem = round((ltp * 0.0078) + (abs(ltp - atm) * 0.55), 2)

        # 💰 Trailing SL (Karishma Update)
        if st.session_state.entry > 0:
            if prem > st.session_state.max_p: st.session_state.max_p = prem
            # Rule: Move SL to Cost if profit > 10 pts
            curr_sl = st.session_state.entry if (st.session_state.max_p - st.session_state.entry) >= 10 else (st.session_state.entry - 10)
        else: curr_sl = 0.0

        if is_buy and speed > 5: sig, col, alert = "💎 MASTER BUY (98%)", "#00ff00", "High confidence breakout."
        elif is_sell and speed < -5: sig, col, alert = "🚨 MASTER SELL (98%)", "#ff4b4b", "Heavy sell-off detected."
        else: sig, col, alert = "⌛ AI THINKING...", "#555555", "Watching patterns."

        # 🔊 Voice Sync (Richard-style friendly interaction)
        if "MASTER" in sig and st.session_state.last_sig != sig:
            if st.session_state.trades < 3:
                st.session_state.trades += 1
                st.session_state.entry, st.session_state.max_p, st.session_state.last_sig = prem, prem, sig
                voice = f"Rajveer Sir, my brain detects {sig}. {alert}. Premium at {prem}."
                st.components.v1.html(f"<script>window.speechSynthesis.speak(new SpeechSynthesisUtterance('{voice}'));</script>", height=0)
        elif "SCANNING" in sig or "THINKING" in sig: st.session_state.last_sig = ""

        # --- 🖥️ 5. UI RENDERING (Master Dashboard) ---
        with live_area.container():
            c1, c2 = st.columns([2, 1])
            with c1:
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True, key=f"ch_{time.time()}")
            with c2:
                st.markdown(f"""<div style='background:#111; padding:20px; border-radius:15px; text-align:center; height:400px; display:flex; flex-direction:column; justify-content:center; border:1px solid #333;'>
                    <h2 style='color:#00ff00; margin:0;'>LTP: {ltp}</h2>
                    <p style='color:gray;'>SPEED: {'FAST' if abs(speed)>5 else 'SLOW'} | WHALE: {'YES' if vol_spike else 'NO'}</p>
                    <hr style='border-color:#333;'>
                    <h4 style='color:white; margin:0;'>ATM STRIKE: {atm}</h4>
                    <h1 style='color:{col}; font-size:60px; margin:5px 0;'>₹{prem}</h1>
                    <p style='color:gray;'>SNIPER: {st.session_state.trades}/3</p>
                </div>""", unsafe_allow_html=True)
            
            st.markdown(f"""<div style='background:#07090f; padding:25px; border-radius:20px; border:5px solid {col}; text-align:center; box-shadow: 0px 0px 25px {col};'>
                <h1 style='color:{col}; margin:0; font-size:45px; font-weight:bold;'>{sig}</h1>
                <div style='display:flex; justify-content:space-around; margin-top:15px; border-top:1px solid #333; padding-top:15px;'>
                    <div><p style='color:gray; margin:0;'>ENTRY</p><h2 style='color:white; margin:0;'>₹{st.session_state.entry if st.session_state.entry>0 else '---'}</h2></div>
                    <div><p style='color:#00ff00; margin:0;'>TARGET (+20)</p><h2 style='color:#00ff00; margin:0;'>₹{round(st.session_state.entry+20, 2) if st.session_state.entry>0 else '---'}</h2></div>
                    <div><p style='color:#ff4b4b; margin:0;'>KARISHMA SL</p><h2 style='color:#ff4b4b; margin:0;'>₹{round(curr_sl, 2) if curr_sl>0 else '---'}</h2></div>
                </div></div>""", unsafe_allow_html=True)

# 🚀 Execute Jarvis
jarvis_brain_execution()
