import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
import warnings
from datetime import datetime

# --- 🎯 1. JARVIS CORE SETUP ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="JARVIS ULTIMATE AI", layout="wide", initial_sidebar_state="collapsed")

# --- 🛡️ 2. PRE-MARKET INTELLIGENCE (Fixed Data Handling) ---
def get_pre_market_report():
    checks = {"GIFT Nifty": "^NSEI", "Nasdaq": "^IXIC", "Reliance": "RELIANCE.NS"}
    results = {}
    for name, sym in checks.items():
        try:
            # Sir, yahan data download fix kiya hai
            hist = yf.download(sym, period="2d", interval="1m", progress=False)
            if not hist.empty:
                # Sirf aakhri closing price le rahe hain taaki ValueError na aaye
                c1 = hist['Close'].iloc[-1]
                c2 = hist['Close'].iloc[-2]
                change = float(((c1 - c2) / c2) * 100)
                results[name] = round(change, 2)
            else: results[name] = 0.0
        except: results[name] = 0.0
    return results

# --- 🔍 3. STATIC UI SETUP ---
st.markdown("<h1 style='text-align:center; color:#00ff00; margin:0;'>🤖 JARVIS ULTIMATE AI</h1>", unsafe_allow_html=True)

# Pre-Market Logic (Error Fixed Line)
pre_report = get_pre_market_report()
# Summing values safely to ensure mood_score is a single float number
mood_score = float(sum(pre_report.values()))
mood_color = "#00ff00" if mood_score > 0 else "#ff4b4b"

st.markdown(f"""<div style='background:#111; padding:10px; border-radius:10px; border-left:5px solid {mood_color}; text-align:center;'>
    Today's Global Forecast: {'BULLISH' if mood_score > 0 else 'BEARISH'} | Global Mood Score: {mood_score}
    </div>""", unsafe_allow_html=True)

# Session States
if "trades" not in st.session_state: st.session_state.trades = 0
if "last_sig" not in st.session_state: st.session_state.last_sig = ""
if "entry" not in st.session_state: st.session_state.entry = 0.0

# --- 🏗️ 4. NO-BLINK LIVE FRAGMENT ---
live_area = st.empty()

@st.fragment(run_every=2)
def jarvis_brain():
    asset = "NIFTY 50" # Default set to Nifty for Rajveer Sir
    ticker = "^NSEI"
    gap = 50
    
    df = yf.download(ticker, period="2d", interval="1m", progress=False, auto_adjust=True)
    
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        ltp = round(float(df['Close'].iloc[-1]), 2)
        
        # 📈 Javed (9/21) + Whale Sensing (E50)
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        df['E50'] = df['Close'].ewm(span=50, adjust=False).mean()
        
        vol_spike = df['Volume'].iloc[-1] > (df['Volume'].rolling(20).mean().iloc[-1] * 1.6)
        
        # Signal Conditions
        is_buy = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (ltp > df['E50'].iloc[-1]) and vol_spike
        is_sell = (df['E9'].iloc[-1] < df['E21'].iloc[-1]) and (ltp < df['E50'].iloc[-1]) and vol_spike
        
        atm = round(ltp / gap) * gap
        prem = round((ltp * 0.0078) + (abs(ltp - atm) * 0.55), 2)

        if is_buy: sig, col = "💎 AI MASTER BUY", "#00ff00"
        elif is_sell: sig, col = "🚨 AI MASTER SELL", "#ff4b4b"
        else: sig, col = "⌛ AI SCANNING...", "#555555"

        # Voice Alerts (Browser Compatible)
        if "MASTER" in sig and st.session_state.last_sig != sig:
            st.session_state.trades += 1
            st.session_state.entry = prem
            st.session_state.last_sig = sig
            st.components.v1.html(f"<script>window.speechSynthesis.speak(new SpeechSynthesisUtterance('{sig} at {prem}'));</script>", height=0)
        elif "SCANNING" in sig: st.session_state.last_sig = ""

        with live_area.container():
            c1, c2 = st.columns([2, 1])
            with c1:
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True, key=f"ch_{time.time()}")
            with c2:
                st.markdown(f"""<div style='background:#111; padding:20px; border-radius:15px; border:1px solid #333; text-align:center; height:400px;'>
                    <h2 style='color:#00ff00;'>LTP: {ltp}</h2>
                    <h4 style='color:white;'>ATM: {atm}</h4><h1 style='color:{col};'>₹{prem}</h1>
                    <p style='color:gray;'>TRADES: {st.session_state.trades}/3</p></div>""", unsafe_allow_html=True)
            
            st.markdown(f"""<div style='background:#07090f; padding:25px; border-radius:20px; border:5px solid {col}; text-align:center;'>
                <h1 style='color:{col}; margin:0; font-size:45px;'>{sig}</h1>
                <div style='display:flex; justify-content:space-around; margin-top:15px;'>
                    <div><p style='color:gray;'>ENTRY</p><h2 style='color:white;'>₹{st.session_state.entry if st.session_state.entry>0 else '---'}</h2></div>
                    <div><p style='color:#00ff00;'>TGT (+20)</p><h2 style='color:#00ff00;'>₹{round(st.session_state.entry+20, 2) if st.session_state.entry>0 else '---'}</h2></div>
                    <div><p style='color:#ff4b4b;'>KARISHMA SL (-10)</p><h2 style='color:#ff4b4b;'>₹{round(st.session_state.entry-10, 2) if st.session_state.entry>0 else '---'}</h2></div>
                </div></div>""", unsafe_allow_html=True)

# 🚀 Execute
jarvis_brain()
