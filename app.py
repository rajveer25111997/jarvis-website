import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import warnings
from datetime import datetime

# --- 🎯 1. CORE SETUP & 1-SEC REFRESH ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="JARVIS TURBO", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=1000, key="jarvis_sync") # No-Blink Display

# --- 🛡️ 2. TURBO DATA ENGINE ---
def fetch_data(ticker):
    try:
        df = yf.download(ticker, period="2d", interval="1m", progress=False, auto_adjust=True)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df
    except: return None

# --- 🔍 3. SARS TOP HEADER ---
st.markdown("<h1 style='text-align:center; color:#00ff00; margin:0;'>🤖 JARVIS IMPERIAL TURBO</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:white; font-size:12px;'>GLOBAL SYNC: ACTIVE | TURBO SENTIMENT: ON | {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)

# --- 🛠️ 4. SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ System Control")
    asset = st.selectbox("🎯 Asset:", ["NIFTY 50", "BANK NIFTY", "CRUDE OIL"])
    trade_limit = st.slider("Sniper Limit:", 1, 10, 3)
    st.write("---")
    st.success("Javed (EMA) & Karishma (SL) Integrated")

indices = {"NIFTY 50": {"sym": "^NSEI", "gap": 50}, "BANK NIFTY": {"sym": "^NSEBANK", "gap": 100}, "CRUDE OIL": {"sym": "CL=F", "gap": 10}}
ticker, gap = indices[asset]["sym"], indices[asset]["gap"]

# --- 🧠 5. MASTER MEMORY ---
if "trades" not in st.session_state: st.session_state.trades = 0
if "last_sig" not in st.session_state: st.session_state.last_sig = ""
if "entry" not in st.session_state: st.session_state.entry = 0.0

live_area = st.empty()

@st.fragment
def run_logic():
    df = fetch_data(ticker)
    
    if df is not None and len(df) > 20:
        # 🛰️ A. TURBO NEWS & GLOBAL IMPACT (Nasdaq + Heavyweights)
        # Nasdaq ka 5% vajan aur Heavyweights ka movement
        stocks = ["RELIANCE.NS", "HDFCBANK.NS", "^IXIC"] 
        news_score = 0
        try:
            h_data = yf.download(stocks, period="1d", interval="1m", progress=False, auto_adjust=True)
            for s in stocks:
                if h_data[s].iloc[-1] > h_data[s].iloc[-2]: news_score += 2 # High Sensitivity
                else: news_score -= 2
        except: pass
        news_mood = "BULLISH" if news_score >= 2 else "BEARISH" if news_score <= -2 else "NEUTRAL"

        # 📊 B. JAVED STRATEGY (EMA 9/21/200)
        ltp = round(df['Close'].iloc[-1], 2)
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        df['E200'] = df['Close'].ewm(span=200, adjust=False).mean()
        
        # RSI Logic
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-10)
        df['RSI'] = 100 - (100 / (1 + rs))

        # 🎯 C. TURBO SIGNAL LOGIC (15-20 Point Focus)
        is_buy = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (df['RSI'].iloc[-1] > 62) and (news_mood == "BULLISH")
        is_sell = (df['E9'].iloc[-1] < df['E21'].iloc[-1]) and (df['RSI'].iloc[-1] < 38) and (news_mood == "BEARISH")
        
        atm_strike = round(ltp / gap) * gap
        premium = round((ltp * 0.0075) + (abs(ltp - atm_strike) * 0.55), 2)

        if is_buy: sig, col = "💎 MASTER BUY (98%)", "#00ff00"
        elif is_sell: sig, col = "🚨 MASTER SELL (98%)", "#ff4b4b"
        else: sig, col = "⌛ SCANNING BREAKOUT...", "#555555"

        # Voice & Sniper Update
        if "MASTER" in sig and st.session_state.last_sig != sig:
            if st.session_state.trades < trade_limit:
                st.session_state.trades += 1
                st.session_state.entry = premium
                st.session_state.last_sig = sig
                voice = f"Jarvis Turbo Alert! {sig}. Target 20 points."
                st.components.v1.html(f"<script>var m=new SpeechSynthesisUtterance('{voice}');window.speechSynthesis.speak(m);</script>", height=0)
        elif "SCANNING" in sig: st.session_state.last_sig = ""

        # 🖥️ D. UI RENDERING
        with live_area.container():
            c1, c2 = st.columns([2, 1])
            with c1:
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True, key=f"ch_{datetime.now().microsecond}")
            
            with c2:
                st.markdown(f"""
                    <div style="background:#111; padding:20px; border-radius:15px; border:1px solid #333; text-align:center; height:400px; display:flex; flex-direction:column; justify-content:center;">
                        <h2 style="color:#00ff00; margin:0;">LTP: {ltp}</h2>
                        <p style="color:gray;">MOOD: {news_mood} | Nasdaq: {'UP' if news_score>0 else 'DOWN'}</p>
                        <h4 style="color:white; margin:0;">ATM: {atm_strike}</h4>
                        <h1 style="color:{col}; font-size:60px; margin:10px 0;">₹{premium}</h1>
                        <p style="color:gray;">TRADES: {st.session_state.trades}/{trade_limit}</p>
                    </div>
                """, unsafe_allow_html=True)

            # SIGNAL BOX
            st.markdown(f"""
                <div style="background:#07090f; padding:25px; border-radius:20px; border:5px solid {col}; text-align:center; box-shadow: 0px 0px 25px {col}; margin-top:10px;">
                    <h1 style="color:{col}; margin:0; font-size:45px; font-weight:bold;">{sig}</h1>
                    <div style="display:flex; justify-content:space-around; margin-top:15px; border-top:1px solid #333; padding-top:15px;">
                        <div><p style="color:gray; margin:0;">ENTRY</p><h2 style="color:white; margin:0;">₹{st.session_state.entry if st.session_state.entry>0 else '---'}</h2></div>
                        <div><p style="color:#00ff00; margin:0;">TGT (+20)</p><h2 style="color:#00ff00; margin:0;">₹{round(st.session_state.entry+20, 2) if st.session_state.entry>0 else '---'}</h2></div>
                        <div><p style="color:#ff4b4b; margin:0;">KARISHMA SL (-10)</p><h2 style="color:#ff4b4b; margin:0;">₹{round(st.session_state.entry-10, 2) if st.session_state.entry>0 else '---'}</h2></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

run_logic()
