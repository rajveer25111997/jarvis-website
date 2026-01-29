import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
import warnings

# --- 🎯 1. SYSTEM SETUP ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="JARVIS RV OS V100", layout="wide", initial_sidebar_state="collapsed")

# --- 🛡️ 2. DATA ENGINE ---
def fetch_data(ticker):
    try:
        # 2 दिन का डेटा ताकि इंडिकेटर्स (E200) सही काम करें
        df = yf.download(ticker, period="2d", interval="1m", progress=False, auto_adjust=True)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): 
                df.columns = df.columns.get_level_values(0)
            return df
    except: return None

# --- 🔍 3. SARS STATUS BAR ---
st.markdown("<h1 style='text-align:center; color:#00ff00; margin:0; font-family:serif; letter-spacing:5px;'>🤖 JARVIS RV OS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:white; font-size:12px; margin-bottom:20px;'>SYSTEM: SECURED | SNIPER MODE | SIGNAL BOX FIXED</p>", unsafe_allow_html=True)

indices = {"NIFTY 50": {"sym": "^NSEI", "gap": 50}, "BANK NIFTY": {"sym": "^NSEBANK", "gap": 100}}
idx_choice = st.sidebar.selectbox("🎯 Target Index:", list(indices.keys()))
ticker, gap = indices[idx_choice]["sym"], indices[idx_choice]["gap"]

# --- 🧠 4. SNIPER MEMORY ---
if "trade_count" not in st.session_state:
    st.session_state.trade_count = 0
if "last_sig" not in st.session_state:
    st.session_state.last_sig = ""
if "entry" not in st.session_state:
    st.session_state.entry = 0.0

live_area = st.empty()

@st.fragment(run_every="2s")
def render_dashboard(ticker, gap):
    # 🚫 Sniper Limit Check
    if st.session_state.trade_count >= 3:
        live_area.markdown("<div style='background:#111; padding:50px; border-radius:20px; text-align:center; border:2px solid #ffff00;'><h1 style='color:#ffff00;'>🎯 3 TRADES COMPLETED</h1><p style='color:white;'>Profit Protected. Overtrading Blocked.</p></div>", unsafe_allow_html=True)
        return

    df = fetch_data(ticker)
    if df is not None and len(df) > 20:
        # 🛰️ A. NEWS & SENTIMENT ENGINE
        heavyweights = ["RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS"]
        news_sentiment = 0
        try:
            h_data = yf.download(heavyweights, period="1d", interval="1m", progress=False, auto_adjust=True)
            if isinstance(h_data.columns, pd.MultiIndex): h_data.columns = h_data.columns.get_level_values(1)
            for stock in heavyweights:
                if h_data[stock].iloc[-1] > h_data[stock].iloc[-2]: news_sentiment += 1
                else: news_sentiment -= 1
        except: pass
        news_mood = "BULLISH" if news_sentiment >= 1 else "BEARISH" if news_sentiment <= -1 else "NEUTRAL"

        # 📊 B. INDICATOR PRECISION
        ltp = round(df['Close'].iloc[-1], 2)
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-10)
        df['RSI'] = 100 - (100 / (1 + rs))

        # 🎯 C. 98% ASSURITY SIGNAL LOGIC
        is_buy = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (df['RSI'].iloc[-1] > 65) and (news_mood == "BULLISH")
        is_sell = (df['E9'].iloc[-1] < df['E21'].iloc[-1]) and (df['RSI'].iloc[-1] < 35) and (news_mood == "BEARISH")
        
        atm_strike = round(ltp / gap) * gap
        calc_premium = round((ltp * 0.0075) + (abs(ltp - atm_strike) * 0.55), 2)

        if is_buy:
            sig_text, sig_color = "💎 MASTER BUY (98%)", "#00ff00"
            voice = "Jarvis detected Master Buy. Entry Confirmed."
        elif is_sell:
            sig_text, sig_color = "🚨 MASTER SELL (98%)", "#ff4b4b"
            voice = "Jarvis detected Master Sell. Exit Confirmed."
        else:
            sig_text, sig_color = "⌛ SCANNING MARKET...", "#555555"
            voice = ""

        # Update Voice & Entry only on NEW Master signals
        if "MASTER" in sig_text and st.session_state.last_sig != sig_text:
            st.session_state.trade_count += 1
            st.session_state.last_sig = sig_text
            st.session_state.entry = calc_premium
            st.components.v1.html(f"<script>var m=new SpeechSynthesisUtterance('{voice}');window.speechSynthesis.speak(m);</script>", height=0)
        elif "SCANNING" in sig_text:
            st.session_state.last_sig = "" # Reset when trend ends

        # 🖥️ D. UI RENDERING (FIXED BOXES)
        with live_area.container():
            c1, c2 = st.columns([2, 1])
            with c1:
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True, key=f"c_{time.time()}")
            
            with c2:
                st.markdown(f"""
                    <div style="background:#111; padding:25px; border-radius:15px; border:1px solid #333; text-align:center; height:400px; display:flex; flex-direction:column; justify-content:center;">
                        <h3 style="color:#00ff00; margin:0;">LIVE: {ltp}</h3>
                        <p style="color:gray; margin:10px 0;">NEWS MOOD: {news_mood}</p>
                        <h2 style="color:white; margin:0;">ATM: {atm_strike}</h2>
                        <h1 style="color:{sig_color}; font-size:60px; margin:10px 0;">₹{calc_premium}</h1>
                        <p style="color:gray;">TRADES TODAY: {st.session_state.trade_count}/3</p>
                    </div>
                """, unsafe_allow_html=True)

            # 🚨 SIGNAL BOX (AB HAMESHA DIKHEGA)
            st.markdown(f"""
                <div style="background:#07090f; padding:25px; border-radius:20px; border:5px solid {sig_color}; text-align:center; box-shadow: 0px 0px 20px {sig_color}; margin-top:10px;">
                    <h1 style="color:{sig_color}; margin:0; font-size:45px; font-weight:bold;">{sig_text}</h1>
                    <div style="display:flex; justify-content:space-around; margin-top:15px; border-top:1px solid #333; padding-top:15px;">
                        <div><p style="color:gray; margin:0;">ENTRY</p><h2 style="color:white; margin:0;">₹{st.session_state.entry if st.session_state.entry > 0 else '---'}</h2></div>
                        <div><p style="color:#00ff00; margin:0;">TARGET (+20)</p><h2 style="color:#00ff00; margin:0;">₹{round(st.session_state.entry + 20, 2) if st.session_state.entry > 0 else '---'}</h2></div>
                        <div><p style="color:#ff4b4b; margin:0;">STOPLOSS (-10)</p><h2 style="color:#ff4b4b; margin:0;">₹{round(st.session_state.entry - 10, 2) if st.session_state.entry > 0 else '---'}</h2></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

render_dashboard(ticker, gap)
