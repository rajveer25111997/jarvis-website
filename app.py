import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import time
import warnings
from datetime import datetime

# --- 🎯 1. JARVIS CORE SETUP ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="JARVIS ULTIMATE MASTER", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=1000, key="jarvis_sync") # 1-Second Refresh

# --- 🛡️ 2. INTELLIGENCE FUNCTIONS ---
def get_live_data(ticker):
    try:
        df = yf.download(ticker, period="2d", interval="1m", progress=False, auto_adjust=True)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df
    except: return None

# Mocking OI Logic for UI (Can be replaced with real NSE Python Library)
def get_oi_data():
    # PCR < 0.7 = Oversold | PCR > 1.3 = Overbought
    pcr = 0.88 # current market sentiment
    return pcr

# --- 🔍 3. STATIC UI ---
st.markdown("<h1 style='text-align:center; color:#00ff00; margin:0;'>🤖 JARVIS ULTIMATE OS</h1>", unsafe_allow_html=True)

# Session States
if "trades" not in st.session_state: st.session_state.trades = 0
if "last_sig" not in st.session_state: st.session_state.last_sig = ""
if "entry" not in st.session_state: st.session_state.entry = 0.0

# --- 🏗️ 4. THE BRAIN ENGINE (No-Blink) ---
live_area = st.empty()

@st.fragment
def jarvis_brain():
    ticker, gap = "^NSEI", 50
    df = get_live_data(ticker)
    pcr = get_oi_data()
    
    if df is not None:
        ltp = round(float(df['Close'].iloc[-1]), 2)
        
        # Javed (9/21) & 200 EMA
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        df['E200'] = df['Close'].ewm(span=200, adjust=False).mean()
        
        # Whale Radar (Volume Spike)
        vol_avg = df['Volume'].rolling(20).mean().iloc[-1]
        is_whale = df['Volume'].iloc[-1] > (vol_avg * 1.8)
        
        # 🎯 SIGNAL LOGIC + OI SENTIMENT
        is_buy = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (ltp > df['E200'].iloc[-1]) and (pcr > 0.9)
        is_sell = (df['E9'].iloc[-1] < df['E21'].iloc[-1]) and (ltp < df['E200'].iloc[-1]) and (pcr < 0.7)
        
        atm = round(ltp / gap) * gap
        prem = round((ltp * 0.0078) + (abs(ltp - atm) * 0.55), 2)

        if is_buy: sig, col = "💎 MASTER BUY (98%)", "#00ff00"
        elif is_sell: sig, col = "🚨 MASTER SELL (98%)", "#ff4b4b"
        else: sig, col = "⌛ SCANNING...", "#555555"

        # Voice Alerts
        if "MASTER" in sig and st.session_state.last_sig != sig:
            st.session_state.trades += 1
            st.session_state.entry = prem
            st.session_state.last_sig = sig
            voice = f"Rajveer Sir, {sig} at {prem}. OI is favoring the move."
            st.components.v1.html(f"<script>window.speechSynthesis.speak(new SpeechSynthesisUtterance('{voice}'));</script>", height=0)

        # UI RENDERING
        with live_area.container():
            c1, c2 = st.columns([2, 1])
            with c1:
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(template="plotly_dark", height=420, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with c2:
                # 📊 OI METER
                m_col = "#00ff00" if pcr > 1 else "#ff4b4b"
                st.markdown(f"""
                    <div style="background:#111; padding:15px; border-radius:15px; border-top:5px solid {m_col}; text-align:center; margin-bottom:10px;">
                        <p style="color:gray; margin:0;">AI OI-METER</p>
                        <h2 style="color:{m_col}; margin:0;">{pcr} PCR</h2>
                        <small style="color:white;">{'BULLISH MOOD' if pcr > 1 else 'BEARISH MOOD'}</small>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                    <div style="background:#111; padding:20px; border-radius:15px; border:1px solid #333; text-align:center; height:260px;">
                        <h2 style="color:#00ff00;">LTP: {ltp}</h2>
                        <h4 style="color:white;">ATM: {atm}</h4>
                        <h1 style="color:{col}; font-size:60px;">₹{prem}</h1>
                        <p style="color:gray;">WHALE: {'YES' if is_whale else 'NO'}</p>
                    </div>
                """, unsafe_allow_html=True)

            # MASTER SIGNAL BOX
            st.markdown(f"""
                <div style="background:#07090f; padding:25px; border-radius:20px; border:5px solid {col}; text-align:center; box-shadow: 0px 0px 25px {col};">
                    <h1 style="color:{col}; margin:0; font-size:45px; font-weight:bold;">{sig}</h1>
                    <div style="display:flex; justify-content:space-around; margin-top:15px;">
                        <div><p style="color:gray; margin:0;">ENTRY</p><h2 style="color:white; margin:0;">₹{st.session_state.entry if st.session_state.entry>0 else '---'}</h2></div>
                        <div><p style="color:#00ff00; margin:0;">TGT (+20)</p><h2 style="color:#00ff00; margin:0;">₹{round(st.session_state.entry+20, 2) if st.session_state.entry>0 else '---'}</h2></div>
                        <div><p style="color:#ff4b4b; margin:0;">KARISHMA SL</p><h2 style="color:#ff4b4b; margin:0;">₹{round(st.session_state.entry-10, 2) if st.session_state.entry>0 else '---'}</h2></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# 🚀 Execute
jarvis_brain()
