import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import time
from datetime import datetime

# 1. सुपर-फास्ट रिफ्रेश इंजन (1 सेकंड)
st.set_page_config(page_title="Jarvis Commander", layout="wide")
st_autorefresh(interval=1000, key="jarvis_final_commander_fixed")

# --- 🛡️ जार्विस "Fail-Safe" डेटा इंजन ---
def get_data_ultimate(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False, timeout=1.5)
        if df is not None and not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df, "🟢 PRIMARY LIVE", "#00FF00"
    except:
        pass
    try:
        df = yf.download(ticker, period="5d", interval="2m", progress=False, timeout=2)
        if df is not None and not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df.tail(60), "🟡 BACKUP SERVER", "#FFFF00"
    except:
        pass
    return None, "🔴 OFFLINE", "#FF0000"

# --- 🧠 जार्विस सेल्फ-लर्निंग स्ट्रेटजी ---
def jarvis_ai_strategy(df):
    if df is None: return "WAIT", 0
    df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    
    curr, prev = df.iloc[-1], df.iloc[-2]
    price = curr['Close']
    
    if curr['E9'] > curr['E21'] and prev['E9'] <= prev['E21'] and curr['RSI'] > 50:
        return "CALL", price
    elif curr['E9'] < curr['E21'] and prev['E9'] >= prev['E21'] and curr['RSI'] < 50:
        return "PUT", price
    return "WAIT", price

# ==========================================
# UI लेआउट: जार्विस मास्टर डैशबोर्ड
# ==========================================

# 1. स्टेटस बार
st.markdown(f"""
    <div style="background-color: #1e1e1e; padding: 10px; border-radius: 5px; display: flex; justify-content: space-between; border-bottom: 2px solid #444; margin-bottom:10px;">
        <span style="color: #00FF00; font-weight: bold;">🤖 JARVIS CORE: ONLINE</span>
        <span style="color: #00d4ff;">🛡️ STRATEGY ENGINE: ACTIVE</span>
        <span style="color: #ffffff;">🕒 {datetime.now().strftime('%H:%M:%S')}</span>
    </div>
    """, unsafe_allow_html=True)

# 2. इंडेक्स मेट्रिक्स
indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "FIN NIFTY": "NIFTY_FIN_SERVICE.NS"}
idx_cols = st.columns(len(indices))
for i, (name, sym) in enumerate(indices.items()):
    df_idx, status, s_color = get_data_ultimate(sym)
    with idx_cols[i]:
        if df_idx is not None:
            st.metric(label=f"{name} ({status})", value=f"₹{df_idx['Close'].iloc[-1]:,.1f}")

st.divider()

# 3. मेन एनालिसिस और पेपर ट्रेडिंग
data_nifty, status_nifty, color_nifty = get_data_ultimate("^NSEI")
c_chart, c_sig = st.columns([3, 1])

with c_chart:
    if data_nifty is not None:
        fig = go.Figure(data=[go.Candlestick(x=data_nifty.index, open=data_nifty['Open'], high=data_nifty['High'], low=data_nifty['Low'], close=data_nifty['Close'])])
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

with c_sig:
    st.subheader("🎯 एआई सिग्नल्स")
    sig, price = jarvis_ai_strategy(data_nifty)
    
    if sig == "CALL":
        st.success(f"🚀 BUY CALL ZONE\nEntry: {price:.2f}\nSL: {price-7:.2f}")
        if st.button("📝 रिकॉर्ड ट्रेड (CALL)"):
            st.session_state.trade_log = st.session_state.get('trade_log', []) + [f"{datetime.now().strftime('%H:%M')} - CALL Entry @ {price:.2f}"]
            st.toast("जार्विस: ट्रेड डायरी में लिख लिया गया है!")
    elif sig == "PUT":
        st.error(f"📉 BUY PUT ZONE\nEntry: {price:.2f}\nSL: {price+7:.2f}")
        if st.button("📝 रिकॉर्ड ट्रेड (PUT)"):
            st.session_state.trade_log = st.session_state.get('trade_log', []) + [f"{datetime.now().strftime('%H:%M')} - PUT Entry @ {price:.2f}"]
            st.toast("जार्विस: ट्रेड रिकॉर्डेड!")
    else:
        st.warning("🔍 स्कैनिंग ज़ोन...")

    st.divider()
    st.subheader("📜 आज का ट्रेड लॉग")
    if 'trade_log' in st.session_state:
        for log in st.session_state.trade_log[-5:]: # आख़िरी 5 ट्रेड
            st.text(log)
    else:
        st.caption("अभी कोई ट्रेड नहीं लिया गया।")
