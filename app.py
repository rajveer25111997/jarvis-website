import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
import warnings

# --- 🎯 1. SYSTEM CONFIG ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="JARVIS RV OS", layout="wide", initial_sidebar_state="collapsed")

# --- 🛡️ 2. DATA ENGINE ---
def fetch_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df
    except: return None

# --- 🔍 3. SARS STATUS BAR (Restored) ---
st.markdown("<h1 style='text-align:center; color:#00ff00; margin:0; font-family:serif; letter-spacing:5px;'>🤖 JARVIS RV OS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:white; font-size:12px; margin-bottom:20px;'>SYSTEM STATUS: SECURED | FRAGMENT MODE ACTIVE | SARS BAR ONLINE</p>", unsafe_allow_html=True)

indices = {"NIFTY 50": {"sym": "^NSEI", "gap": 50}, "BANK NIFTY": {"sym": "^NSEBANK", "gap": 100}}
idx_choice = st.sidebar.selectbox("🎯 Index Selector:", list(indices.keys()))
ticker = indices[idx_choice]["sym"]
gap = indices[idx_choice]["gap"]

# --- 🏗️ 4. LIVE AREA ---
live_area = st.empty()

@st.fragment(run_every="2s")
def render_dashboard(ticker, gap):
    df = fetch_data(ticker)
    if df is not None and not df.empty:
        ltp = round(df['Close'].iloc[-1], 2)
        atm_strike = round(ltp / gap) * gap
        momentum = df['Close'].diff(3).iloc[-1] if len(df) > 3 else 0

        # Precision Math Model
        base_val = ltp * 0.007 
        dist_factor = abs(ltp - atm_strike) * 0.52
        calculated_premium = round(base_val + dist_factor + (momentum * 4), 2)
        
        # 9/21 EMA Strategy
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        is_buy = df['E9'].iloc[-1] > df['E21'].iloc[-1]
        sig_text = "BUY (CALL)" if is_buy else "SELL (PUT)"
        sig_color = "#00ff00" if is_buy else "#ff4b4b"

        if "entry_price" not in st.session_state or st.session_state.active_sig != sig_text:
            st.session_state.entry_price = calculated_premium
            st.session_state.active_sig = sig_text

        with live_area.container():
            # 📊 Main Dashboard
            c1, c2 = st.columns([2, 1])
            with c1:
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True, key=f"c_{time.time()}")
            
            with c2:
                st.markdown(f"""
                    <div style="background:#111; padding:25px; border-radius:15px; border:1px solid #333; text-align:center; height:400px; display:flex; flex-direction:column; justify-content:center;">
                        <h2 style="color:white; margin:0;">ATM: {atm_strike}</h2>
                        <h1 style="color:{sig_color}; font-size:60px; margin:10px 0;">₹{calculated_premium}</h1>
                        <p style="color:white; font-size:18px;">CALCULATED PREMIUM</p>
                    </div>
                """, unsafe_allow_html=True)

            # 🚨 SIGNAL BOX
            st.markdown(f"""
                <div style="background:#07090f; padding:25px; border-radius:20px; border:5px solid {sig_color}; text-align:center; box-shadow: 0px 0px 20px {sig_color}; margin-top:10px;">
                    <h1 style="color:{sig_color}; margin:0; font-size:45px; font-weight:bold;">{sig_text} ACTIVE</h1>
                    <div style="display:flex; justify-content:space-around; margin-top:15px; border-top:1px solid #333; padding-top:15px;">
                        <div><p style="color:gray; margin:0;">ENTRY</p><h2 style="color:white; margin:0;">₹{st.session_state.entry_price}</h2></div>
                        <div><p style="color:#00ff00; margin:0;">TARGET</p><h2 style="color:#00ff00; margin:0;">₹{round(st.session_state.entry_price + 18, 2)}</h2></div>
                        <div><p style="color:#ff4b4b; margin:0;">STOPLOSS</p><h2 style="color:#ff4b4b; margin:0;">₹{round(st.session_state.entry_price - 8, 2)}</h2></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

render_dashboard(ticker, gap)

# --- 🛰️ 5. AI STOCK ANALYSIS LIST (Restored) ---
st.write("---")
st.markdown("<h3 style='color:white; font-family:serif;'>🛰️ JARVIS AI STOCK SCANNER</h3>", unsafe_allow_html=True)
sc1, sc2, sc3 = st.columns(3)
# Aapki list se uthaye gaye top trending stocks
stocks = [("RELIANCE", "Bullish"), ("HDFC BANK", "Strong Buy"), ("COAL INDIA", "BCCL IPO Focus")]

for i, (name, trend) in enumerate(stocks):
    t_color = "#00ff00" if "Buy" in trend or "Bullish" in trend else "#ffff00"
    with [sc1, sc2, sc3][i]:
        st.markdown(f"""
            <div style="background:#111; padding:15px; border-radius:12px; border-left:8px solid {t_color};">
                <h4 style="margin:0; color:white;">{name}</h4>
                <p style="margin:0; color:{t_color}; font-weight:bold;">{trend}</p>
            </div>
        """, unsafe_allow_html=True)
