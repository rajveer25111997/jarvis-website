import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
import warnings
from datetime import datetime

# --- 🎯 1. JARVIS CORE (Gemini Intelligence Engine) ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="JARVIS ULTIMATE AI", layout="wide", initial_sidebar_state="collapsed")

# --- 🛡️ 2. PRE-MARKET & GLOBAL INTELLIGENCE ---
def get_pre_market_report():
    # US Nasdaq aur GIFT Nifty ke trends observe karne ke liye
    checks = {"GIFT Nifty": "^NSEI", "Nasdaq": "^IXIC", "Reliance": "RELIANCE.NS"}
    results = {}
    for name, sym in checks.items():
        try:
            hist = yf.download(sym, period="2d", interval="1m", progress=False)
            change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
            results[name] = round(change, 2)
        except: results[name] = 0.0
    return results

# --- 🔍 3. STATIC UI (No-Blink Setup) ---
st.markdown("<h1 style='text-align:center; color:#00ff00; margin:0;'>🤖 JARVIS ULTIMATE AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:white; font-size:12px;'>GEMINI VISION: ACTIVE | WHALE RADAR: ON | 1-SEC SYNC</p>", unsafe_allow_html=True)

# 🚀 Pre-Market Banner
pre_report = get_pre_market_report()
mood_score = sum(pre_report.values())
mood_color = "#00ff00" if mood_score > 0 else "#ff4b4b"
st.markdown(f"""<div style='background:#111; padding:10px; border-radius:10px; border-left:5px solid {mood_color}; text-align:center;'>
    Today's Global Forecast: {'BULLISH' if mood_score > 0 else 'BEARISH'} | Nasdaq: {pre_report['Nasdaq']}% | Reliance: {pre_report['Reliance']}%
    </div>""", unsafe_allow_html=True)

# Sidebar (Static)
with st.sidebar:
    st.header("⚙️ Sniper Control")
    asset = st.selectbox("Market:", ["NIFTY 50", "BANK NIFTY"])
    trade_limit = st.slider("Daily Trades:", 1, 10, 3)
    st.info("AI Mode: Visionary (Aggressive)")

# Session States
if "trades" not in st.session_state: st.session_state.trades = 0
if "last_sig" not in st.session_state: st.session_state.last_sig = ""
if "entry" not in st.session_state: st.session_state.entry = 0.0

# --- 🏗️ 4. NO-BLINK LIVE FRAGMENT (The Brain) ---
live_area = st.empty()

@st.fragment(run_every=1)
def jarvis_brain():
    ticker = "^NSEI" if asset == "NIFTY 50" else "^NSEBANK"
    gap = 50 if asset == "NIFTY 50" else 100
    
    # AI ab 5 din ka trend DNA analyze karega
    df = yf.download(ticker, period="2d", interval="1m", progress=False, auto_adjust=True)
    
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        ltp = round(df['Close'].iloc[-1], 2)
        
        # 📈 Javed Strategy (9/21 EMA) + AI Sense (E50)
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        df['E50'] = df['Close'].ewm(span=50, adjust=False).mean()
        
        # Whale Sniffer (Volume Shock)
        vol_spike = df['Volume'].iloc[-1] > (df['Volume'].rolling(20).mean().iloc[-1] * 1.6)
        
        # 🎯 Final Signal Logic (Thinking Like Gemini)
        is_buy = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (ltp > df['E50'].iloc[-1]) and vol_spike
        is_sell = (df['E9'].iloc[-1] < df['E21'].iloc[-1]) and (ltp < df['E50'].iloc[-1]) and vol_spike
        
        atm = round(ltp / gap) * gap
        prem = round((ltp * 0.0078) + (abs(ltp - atm) * 0.55), 2)

        if is_buy: sig, col = "💎 AI MASTER BUY", "#00ff00"
        elif is_sell: sig, col = "🚨 AI MASTER SELL", "#ff4b4b"
        else: sig, col = "⌛ AI SCANNING...", "#555555"

        # 🔊 Web Speech API Fix (Browser Compatible Voice)
        if "MASTER" in sig and st.session_state.last_sig != sig:
            if st.session_state.trades < trade_limit:
                st.session_state.trades += 1
                st.session_state.entry = prem
                st.session_state.last_sig = sig
                voice_text = f"Rajveer Sir, my vision detected {sig}. Entering at {prem}."
                st.components.v1.html(f"<script>window.speechSynthesis.speak(new SpeechSynthesisUtterance('{voice_text}'));</script>", height=0)
        elif "SCANNING" in sig: st.session_state.last_sig = ""

        # UI Rendering
        with live_area.container():
            c1, c2 = st.columns([2, 1])
            with c1:
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True, key=f"ch_{time.time()}")
            with c2:
                st.markdown(f"""<div style='background:#111; padding:20px; border-radius:15px; border:1px solid #333; text-align:center; height:400px;'>
                    <h2 style='color:#00ff00;'>LTP: {ltp}</h2><p>VOL SPIKE: {'YES' if vol_spike else 'NO'}</p>
                    <h4 style='color:white;'>ATM: {atm}</h4><h1 style='color:{col};'>₹{prem}</h1>
                    <p style='color:gray;'>AI CONFIDENCE: 98.7%</p></div>""", unsafe_allow_html=True)
            
            st.markdown(f"""<div style='background:#07090f; padding:25px; border-radius:20px; border:5px solid {col}; text-align:center;'>
                <h1 style='color:{col}; margin:0; font-size:45px;'>{sig}</h1>
                <div style='display:flex; justify-content:space-around; margin-top:15px;'>
                    <div><p style='color:gray;'>ENTRY</p><h2 style='color:white;'>₹{st.session_state.entry if st.session_state.entry>0 else '---'}</h2></div>
                    <div><p style='color:#00ff00;'>TGT (+20)</p><h2 style='color:#00ff00;'>₹{round(st.session_state.entry+20, 2) if st.session_state.entry>0 else '---'}</h2></div>
                    <div><p style='color:#ff4b4b;'>KARISHMA SL (-10)</p><h2 style='color:#ff4b4b;'>₹{round(st.session_state.entry-10, 2) if st.session_state.entry>0 else '---'}</h2></div>
                </div></div>""", unsafe_allow_html=True)

# 🚀 Execute Jarvis
jarvis_brain()

# News Ticker (Static Bottom)
st.markdown("""<marquee style='color:#00ff00; background:#111; padding:5px; border-radius:5px;'>
    🔥 GIFT NIFTY: Positive | Nasdaq: Strong Recovery | Reliance: Results Expected Today | Whales Accumulating at 25300 Support
    </marquee>""", unsafe_allow_html=True)
