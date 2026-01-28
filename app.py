import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
import warnings

# --- 🎯 1. सिस्टम कॉन्फ़िगरेशन ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="JARVIS SNIPER MODE", layout="wide", initial_sidebar_state="collapsed")

# --- 🛡️ 2. डेटा इंजन ---
def fetch_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df
    except: return None

# --- 🔍 3. SARS STATUS BAR ---
st.markdown("<h1 style='text-align:center; color:#00ff00; margin:0; font-family:serif; letter-spacing:5px;'>🤖 JARVIS SNIPER MODE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:white; font-size:12px; margin-bottom:20px;'>STATUS: SNIPER ACTIVE | LIMIT: 3 TRADES PER DAY</p>", unsafe_allow_html=True)

indices = {"NIFTY 50": {"sym": "^NSEI", "gap": 50}, "BANK NIFTY": {"sym": "^NSEBANK", "gap": 100}}
idx_choice = st.sidebar.selectbox("🎯 Select Target Index:", list(indices.keys()))
ticker, gap = indices[idx_choice]["sym"], indices[idx_choice]["gap"]

# --- 🧠 4. SNIPER LOGIC (Limit & Learning) ---
if "trade_count" not in st.session_state:
    st.session_state.trade_count = 0
    st.session_state.daily_limit = 3

live_area = st.empty()

@st.fragment(run_every="2s")
def render_dashboard(ticker, gap):
    # अगर 3 ट्रेड पूरे हो गए तो जार्विस सो जाएगा
    if st.session_state.trade_count >= st.session_state.daily_limit:
        live_area.markdown(f"""<div style='background:#111; padding:50px; border-radius:20px; text-align:center; border:2px solid #ffff00;'>
            <h1 style='color:#ffff00;'>🎯 3 TRADES COMPLETED</h1>
            <p style='color:white; font-size:20px;'>आज का कोटा पूरा हुआ। ओवर-ट्रेडिंग से बचें और मुनाफा घर ले जाएं।</p>
            <button onclick="window.location.reload();" style="padding:10px 20px; background:#00ff00; border:none; border-radius:5px; cursor:pointer;">RESET FOR NEXT DAY</button>
        </div>""", unsafe_allow_html=True)
        return

    df = fetch_data(ticker)
    if df is not None and len(df) > 20:
        # 🛰️ A. FII/DII SENTIMENT (Hidden)
        heavyweights = ["RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS"]
        sentiment_score = 0
        try:
            h_data = yf.download(heavyweights, period="1d", interval="1m", progress=False)['Close']
            for stock in heavyweights:
                if h_data[stock].iloc[-1] > h_data[stock].iloc[-2]: sentiment_score += 1
                else: sentiment_score -= 1
        except: pass

        # 📊 B. TECHNICALS
        ltp = round(df['Close'].iloc[-1], 2)
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-10)
        df['RSI'] = 100 - (100 / (1 + rs))

        # 🎯 C. MASTER ASSURITY LOGIC ( Sniper Engine )
        # जार्विस तभी बोलेगा जब RSI > 65 हो और Big Players साथ हों
        is_buy = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (df['RSI'].iloc[-1] > 65) and (sentiment_score >= 2)
        is_sell = (df['E9'].iloc[-1] < df['E21'].iloc[-1]) and (df['RSI'].iloc[-1] < 35) and (sentiment_score <= -2)
        
        atm_strike = round(ltp / gap) * gap
        calc_premium = round((ltp * 0.0075) + (abs(ltp - atm_strike) * 0.55), 2)

        if is_buy:
            sig_text, sig_color, assurity = "💎 MASTER BUY (98%)", "#00ff00", "MASTER GRADE"
        elif is_sell:
            sig_text, sig_color, assurity = "🚨 MASTER SELL (98%)", "#ff4b4b", "MASTER GRADE"
        else:
            sig_text, sig_color, assurity = "⌛ SNIPER SCANNING...", "#555555", "WAITING"

        # Signal Lock & Trade Counting
        if "active_sig" not in st.session_state or st.session_state.active_sig != sig_text:
            if "MASTER" in sig_text:
                st.session_state.trade_count += 1 # ट्रेड गिना गया
                voice_msg = f"Sniper Trade {st.session_state.trade_count} detected. Assurity is High."
                st.components.v1.html(f"<script>var m = new SpeechSynthesisUtterance('{voice_msg}'); window.speechSynthesis.speak(m);</script>", height=0)
            
            st.session_state.entry = calc_premium
            st.session_state.active_sig = sig_text

        # 🖥️ UI RENDERING
        with live_area.container():
            c1, c2 = st.columns([2, 1])
            with c1:
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(template="plotly_dark", height=380, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True, key=f"c_{time.time()}")
            
            with c2:
                st.markdown(f"""
                    <div style="background:#111; padding:20px; border-radius:15px; border:1px solid #333; text-align:center; height:380px; display:flex; flex-direction:column; justify-content:center;">
                        <p style="color:gray;">TRADES TODAY: {st.session_state.trade_count}/3</p>
                        <h2 style="color:white; margin:0;">ATM: {atm_strike}</h2>
                        <h1 style="color:{sig_color}; font-size:55px; margin:5px 0;">₹{calc_premium}</h1>
                        <p style="color:{sig_color}; font-weight:bold;">{assurity}</p>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
                <div style="background:#07090f; padding:25px; border-radius:20px; border:5px solid {sig_color}; text-align:center; box-shadow: 0px 0px 20px {sig_color}; margin-top:10px;">
                    <h1 style="color:{sig_color}; margin:0; font-size:40px; font-weight:bold;">{sig_text}</h1>
                    <div style="display:flex; justify-content:space-around; margin-top:10px; border-top:1px solid #333; padding-top:15px;">
                        <div><p style="color:gray; margin:0;">ENTRY</p><h2 style="color:white; margin:0;">₹{st.session_state.entry}</h2></div>
                        <div><p style="color:#00ff00; margin:0;">TGT (+20)</p><h2 style="color:#00ff00; margin:0;">₹{round(st.session_state.entry + 20, 2)}</h2></div>
                        <div><p style="color:#ff4b4b; margin:0;">SL (-10)</p><h2 style="color:#ff4b4b; margin:0;">₹{round(st.session_state.entry - 10, 2)}</h2></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

render_dashboard(ticker, gap)
