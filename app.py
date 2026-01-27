import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz
import base64

# --- 🎯 पॉइंट 44: 1-सेकंड डेटा पल्स (The Heartbeat) ---
st.set_page_config(page_title="JARVIS RV MASTER 1S", layout="wide")
from streamlit_autorefresh import st_autorefresh

# अंतराल को 1000ms (1 सेकंड) पर सेट किया गया है
st_autorefresh(interval=1000, key="jarvis_turbo_pulse")

def get_ist():
    return datetime.now(pytz.timezone('Asia/Kolkata'))

@st.cache_data(ttl=1) # कैश को भी 1 सेकंड के लिए सेट किया है
def fetch_master_data(ticker):
    try:
        # पॉइंट 38: सुपर फास्ट डेटा हंटर
        df = yf.download(ticker, period="1d", interval="1m", progress=False, timeout=2)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df, "🟢 LIVE 1S"
    except:
        return None, "🔴 DELAYED"

# --- डैशबोर्ड हेडर ---
ist_now = get_ist()
ticker = "^NSEI" 
df, d_status = fetch_master_data(ticker)

st.markdown(f"""
    <div style="background-color:#0e1117; padding:10px; border-radius:10px; border-bottom:3px solid #ff0000; display:flex; justify-content:space-between;">
        <span style="color:#ff0000; font-weight:bold; font-size:22px;">🤖 JARVIS TURBO 1S</span>
        <span style="color:white; font-weight:bold;">🕒 {ist_now.strftime('%I:%M:%S %p')} | 🛡️ 44 POINTS ACTIVE</span>
    </div>
""", unsafe_allow_html=True)

if df is not None and len(df) > 20:
    # गणना इंजन (जावेद EMA 9/21 + RSI)
    df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    curr, prev = df.iloc[-1], df.iloc[-2]
    ltp = round(curr['Close'], 2)
    
    # स्मार्ट स्ट्राइक और SL/TGT (पॉइंट 42)
    atm_strike = round(ltp / 50) * 50
    sl_val = round(ltp - 25, 2)
    tgt_val = round(ltp + 55, 2)
    
    # सिग्नल और इमरजेंसी साउंड (पॉइंट 43)
    sig, sig_color = "WAIT", "#333"
    if curr['E9'] > curr['E21'] and prev['E9'] <= prev['E21']:
        sig, sig_color = "BUY", "#00ff00"
        st.balloons()
        st.markdown(f'<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mp3"></audio>', unsafe_allow_html=True)
    elif curr['E9'] < curr['E21'] and prev['E9'] >= prev['E21']:
        sig, sig_color = "SELL", "#ff4b4b"
        st.markdown(f'<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mp3"></audio>', unsafe_allow_html=True)

    # जैकपॉट डिस्प्ले
    st.markdown(f"""
        <div style="background-color:#1e2130; padding:20px; border-radius:15px; border-left:10px solid {sig_color}; margin-top:10px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <h1 style="color:white; margin:0;">NIFTY: {ltp}</h1>
                    <h2 style="color:{sig_color}; margin:0;">{sig} SIGNAL</h2>
                </div>
                <div style="text-align:right;">
                    <p style="color:#00ff00; font-size:20px; margin:0;">🎯 TGT: {tgt_val}</p>
                    <p style="color:#ff4b4b; font-size:20px; margin:0;">🛡️ SL: {sl_val}</p>
                    <p style="color:#ffaa00; font-size:22px; font-weight:bold;">💎 TRADE: {atm_strike} {'CE' if sig != 'SELL' else 'PE'}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_chart, col_side = st.columns([3, 1])
    
    with col_chart:
        # पॉइंट 41: स्टेबल चार्टिंग (No Blinking)
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.add_trace(go.Scatter(x=df.index, y=df['E9'], line=dict(color='orange', width=1.5), name="EMA 9"))
        fig.add_trace(go.Scatter(x=df.index, y=df['E21'], line=dict(color='cyan', width=1.5), name="EMA 21"))
        
        # विजुअल SL/TGT (पॉइंट 39)
        fig.add_hline(y=tgt_val, line_dash="dash", line_color="green", annotation_text="Target")
        fig.add_hline(y=sl_val, line_dash="dash", line_color="red", annotation_text="Stop Loss")
        
        fig.update_layout(template="plotly_dark", height=550, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with col_side:
        # पॉइंट 13, 30, 33: कंट्रोल रूम
        st.subheader("🛡️ रिस्क मैनेजर")
        risk = st.number_input("Risk Capital:", 500)
        st.metric("Lots", max(1, (risk//25)))
        
        st.divider()
        st.subheader("🐳 व्हेल रडार")
        vol_check = df['Volume'].iloc[-1] > df['Volume'].tail(10).mean()
        st.write("वॉल्यूम एक्टिविटी: " + ("✅ IN" if vol_check else "⏳ WAIT"))
        
        st.divider()
        st.subheader("🩺 पोर्टफोलियो")
        st.caption("RVNL & TATA STEEL: ✅ HOLD")
        st.write(f"Status: {d_status}")

else:
    st.warning("⏳ जार्विस 1-सेकंड डेटा लिंक जोड़ रहा है... कृपया इंतज़ार करें।")

st.caption("Jarvis RV OS v16.0 | 1-Second Turbo Pulse | 44 Points Master")
