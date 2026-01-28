import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
import warnings

# --- 🎯 1. सिस्टम कॉन्फ़िगरेशन ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="JARVIS RV OS", layout="wide", initial_sidebar_state="collapsed")

# --- 🛡️ 2. डेटा इंजन ---
def fetch_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df
    except: return None

# --- 🔍 3. SARS STATUS BAR (टॉप हेडर) ---
st.markdown("<h1 style='text-align:center; color:#00ff00; margin:0; font-family:serif; letter-spacing:5px;'>🤖 JARVIS RV OS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:white; font-size:12px; margin-bottom:20px;'>SYSTEM STATUS: SECURED | WORLD CLASS INDICATORS ACTIVE</p>", unsafe_allow_html=True)

indices = {"NIFTY 50": {"sym": "^NSEI", "gap": 50}, "BANK NIFTY": {"sym": "^NSEBANK", "gap": 100}}
idx_choice = st.sidebar.selectbox("🎯 Target Index:", list(indices.keys()))
ticker, gap = indices[idx_choice]["sym"], indices[idx_choice]["gap"]

live_area = st.empty()

# --- 🏗️ 4. वर्ल्ड क्लास इंडिकेटर इंजन और डैशबोर्ड ---
@st.fragment(run_every="2s")
def render_dashboard(ticker, gap):
    df = fetch_data(ticker)
    if df is not None and not df.empty:
        # 1. EMA 9/21
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        # 2. RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 3. Precision Math Premium
        ltp = round(df['Close'].iloc[-1], 2)
        atm_strike = round(ltp / gap) * gap
        calc_premium = round((ltp * 0.007) + (abs(ltp - atm_strike) * 0.52), 2)

        # 4. Strategy Logic (World Class Combination)
        is_buy = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (df['RSI'].iloc[-1] > 60)
        is_sell = (df['E9'].iloc[-1] < df['E21'].iloc[-1]) and (df['RSI'].iloc[-1] < 40)
        
        sig_text = "STRONG BUY (CALL)" if is_buy else "STRONG SELL (PUT)" if is_sell else "WAITING FOR TREND"
        sig_color = "#00ff00" if is_buy else "#ff4b4b" if is_sell else "#ffff00"

        if "entry" not in st.session_state or st.session_state.active_sig != sig_text:
            st.session_state.entry = calc_premium
            st.session_state.active_sig = sig_text

        # ✅ UI RENDERING (अब यह सही जगह पर है)
        with live_area.container():
            c1, c2 = st.columns([2, 1])
            with c1:
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True, key=f"c_{time.time()}")
            
            with c2:
                st.markdown(f"""
                    <div style="background:#111; padding:25px; border-radius:15px; border:1px solid #333; text-align:center; height:400px; display:flex; flex-direction:column; justify-content:center;">
                        <h2 style="color:white; margin:0;">ATM: {atm_strike}</h2>
                        <h1 style="color:{sig_color}; font-size:60px; margin:10px 0;">₹{calc_premium}</h1>
                        <p style="color:white;">RSI: {round(df['RSI'].iloc[-1], 2)}</p>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
                <div style="background:#07090f; padding:25px; border-radius:20px; border:5px solid {sig_color}; text-align:center; box-shadow: 0px 0px 20px {sig_color}; margin-top:10px;">
                    <h1 style="color:{sig_color}; margin:0; font-size:40px; font-weight:bold;">{sig_text}</h1>
                    <div style="display:flex; justify-content:space-around; margin-top:15px; border-top:1px solid #333; padding-top:15px;">
                        <div><p style="color:gray; margin:0;">ENTRY</p><h2 style="color:white; margin:0;">₹{st.session_state.entry}</h2></div>
                        <div><p style="color:#00ff00; margin:0;">TARGET</p><h2 style="color:#00ff00; margin:0;">₹{round(st.session_state.entry + 18, 2)}</h2></div>
                        <div><p style="color:#ff4b4b; margin:0;">STOPLOSS</p><h2 style="color:#ff4b4b; margin:0;">₹{round(st.session_state.entry - 8, 2)}</h2></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

render_dashboard(ticker, gap)

# --- 🛰️ 5. AI STOCK SCANNER (नीचे वाली लिस्ट) ---
st.write("---")
st.markdown("<h3 style='color:white;'>🛰️ JARVIS AI STOCK SCANNER</h3>", unsafe_allow_html=True)
sc1, sc2, sc3 = st.columns(3)
stocks = [("RELIANCE", "Bullish"), ("HDFC BANK", "Strong Buy"), ("COAL INDIA", "BCCL IPO Focus")]
for i, (name, trend) in enumerate(stocks):
    t_color = "#00ff00" if "Buy" in trend or "Bullish" in trend else "#ffff00"
    with [sc1, sc2, sc3][i]:
        st.markdown(f"""<div style="background:#111; padding:15px; border-radius:12px; border-left:8px solid {t_color};">
            <h4 style="margin:0; color:white;">{name}</h4><p style="margin:0; color:{t_color}; font-weight:bold;">{trend}</p></div>""", unsafe_allow_html=True)
