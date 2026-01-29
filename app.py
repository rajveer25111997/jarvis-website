import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
import warnings

# --- 🎯 1. CORE SETUP ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="JARVIS TURBO V107", layout="wide", initial_sidebar_state="collapsed")

# --- 🛡️ 2. DATA ENGINE ---
def fetch_data(ticker):
    try:
        df = yf.download(ticker, period="2d", interval="1m", progress=False, auto_adjust=True)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df
    except: return None

# --- 🔍 3. STATIC UI ---
st.markdown("<h1 style='text-align:center; color:#00ff00; margin:0;'>🤖 JARVIS IMPERIAL OS</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Sniper Control")
    asset = st.selectbox("🎯 Asset:", ["NIFTY 50", "BANK NIFTY"])
    mode = st.radio("Mode:", ["Safe", "Turbo (Aggressive)"])

# --- 🏗️ 4. NO-BLINK LIVE AREA (The Fragment) ---
live_area = st.empty()

@st.fragment(run_every=2)
def refresh_dashboard():
    indices = {"NIFTY 50": {"sym": "^NSEI", "gap": 50}, "BANK NIFTY": {"sym": "^NSEBANK", "gap": 100}}
    ticker, gap = indices[asset]["sym"], indices[asset]["gap"]
    
    df = fetch_data(ticker)
    
    if df is not None and len(df) > 20:
        # 📈 CALCULATION
        ltp = round(df['Close'].iloc[-1], 2)
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        # 🌊 VOLUME SHOCK LOGIC (For catching rallies early)
        vol_avg = df['Volume'].rolling(20).mean().iloc[-1]
        is_vol_spike = df['Volume'].iloc[-1] > (vol_avg * 1.8)
        
        # 🎯 SIGNAL (Reduced RSI filter for Aggressive mode)
        rsi_limit = 58 if mode == "Turbo (Aggressive)" else 65
        is_buy = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (is_vol_spike or ltp > df['E21'].iloc[-1])
        
        # 💰 PREMIUM & TARGET
        atm = round(ltp / gap) * gap
        prem = round((ltp * 0.0075) + (abs(ltp - atm) * 0.55), 2)

        if is_buy: sig, col = "💎 MASTER BUY", "#00ff00"
        else: sig, col = "⌛ SCANNING...", "#555555"

        with live_area.container():
            c1, c2 = st.columns([2, 1])
            with c1:
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True, key=f"ch_{time.time()}")
            
            with c2:
                st.markdown(f"""
                    <div style="background:#111; padding:20px; border-radius:15px; border:1px solid #333; text-align:center; height:400px; display:flex; flex-direction:column; justify-content:center;">
                        <h2 style="color:#00ff00;">LTP: {ltp}</h2>
                        <p style="color:gray;">VOL SPIKE: {'YES' if is_vol_spike else 'NO'}</p>
                        <h4 style="color:white;">ATM: {atm}</h4>
                        <h1 style="color:{col}; font-size:60px;">₹{prem}</h1>
                        <p style="color:gray;">JARVIS READY</p>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
                <div style="background:#07090f; padding:25px; border-radius:20px; border:5px solid {col}; text-align:center;">
                    <h1 style="color:{col}; margin:0; font-size:45px;">{sig}</h1>
                    <div style="display:flex; justify-content:space-around; margin-top:15px;">
                        <div><p style="color:gray;">ENTRY</p><h2 style="color:white;">₹{prem if is_buy else '---'}</h2></div>
                        <div><p style="color:#00ff00;">TGT (+20)</p><h2 style="color:#00ff00;">₹{prem+20 if is_buy else '---'}</h2></div>
                        <div><p style="color:#ff4b4b;">SL (-10)</p><h2 style="color:#ff4b4b;">₹{prem-10 if is_buy else '---'}</h2></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# 🚀 LAUNCH
refresh_dashboard()
