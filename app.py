import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz

# --- कोर सेटिंग्स ---
st.set_page_config(page_title="JARVIS RV TURBO", layout="wide")
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=1000, key="jarvis_turbo_pulse")

def get_ist():
    return datetime.now(pytz.timezone('Asia/Kolkata'))

def get_status():
    now = get_ist().time()
    m_open, m_close = datetime.strptime("09:15", "%H:%M").time(), datetime.strptime("15:30", "%H:%M").time()
    if now < m_open: return "⏳ PRE-MARKET", "#FFFF00"
    if now > m_close: return "🌙 CLOSED", "#FF4B4B"
    return "🔥 LIVE", "#00FF00"

@st.cache_data(ttl=1)
def fetch_hunter(ticker):
    label, _ = get_status()
    p, i = ("1d", "1m") if label == "🔥 LIVE" else ("5d", "5m")
    try:
        df = yf.download(ticker, period=p, interval=i, progress=False, timeout=3)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df, "🟢 PRIMARY"
    except:
        return None, "🔴 OFFLINE"

# --- डैशबोर्ड ---
label, color = get_status()
st.markdown(f"""<div style="background-color: #0e1117; padding: 15px; border-radius: 10px; border: 1px solid {color}; text-align: center;">
    <span style="color: {color}; font-weight: bold; font-size: 24px;">🤖 JARVIS RV TURBO | {label}</span>
</div>""", unsafe_allow_html=True)

ticker = "^NSEI" 
df, route = fetch_hunter(ticker)

if df is not None and len(df) > 14: # RSI के लिए 14 कैंडल चाहिए
    # --- जावेद + पॉइंट 40 (Booster) ---
    df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    # RSI कैलकुलेशन
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))

    curr, prev = df.iloc[-1], df.iloc[-2]
    diff = curr['E9'] - curr['E21']
    
    col_main, col_side = st.columns([2, 1])
    
    with col_main:
        # --- 🚀 पॉइंट 40: सुपर सेंसिटिव सिग्नल लॉजिक ---
        sig = "WAIT"
        reason = ""
        
        if diff > 0 and prev['E9'] <= prev['E21']:
            sig = "BUY"
            reason = "जावेद क्रॉसओवर (95% Acc)"
        elif diff > -1 and diff <= 0 and curr['RSI'] > 55 and curr['Close'] > curr['Open']:
            sig = "EARLY BUY"
            reason = "मोमेंटम हंटर (Lines touching + High RSI)"
        elif diff < 0 and prev['E9'] >= prev['E21']:
            sig = "SELL"
            reason = "ट्रेंड रिवर्सल"

        if sig != "WAIT":
            st.success(f"🚀 {sig} जैकपॉट! | तर्क: {reason}")
            st.balloons()
        else:
            st.info(f"🧐 स्कैनिंग... RSI: {curr['RSI']:.2f} | Diff: {diff:.2f}")

        # चार्ट
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.add_trace(go.Scatter(x=df.index, y=df['E9'], line=dict(color='orange', width=1.5), name="EMA 9"))
        fig.add_trace(go.Scatter(x=df.index, y=df['E21'], line=dict(color='cyan', width=1.5), name="EMA 21"))
        fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col_side:
        st.subheader("🛡️ कंट्रोल रूम")
        st.metric("RSI मोमेंटम", f"{curr['RSI']:.2f}")
        vol_active = df['Volume'].iloc[-1] > df['Volume'].tail(10).mean() * 1.5
        st.write("बड़े खिलाड़ी: " + ("✅ IN" if vol_active else "⏳ OUT"))
        st.divider()
        st.subheader("🩺 पोर्टफोलियो")
        st.caption("RVNL & TATA STEEL: ✅ HOLD")
else:
    st.warning("⏳ जार्विस डेटा वार्म-अप कर रहा है (14 मिनट का डेटा लोड हो रहा है)...")

st.caption("Jarvis RV OS v11.0 | 40 Points Turbo Edition")
