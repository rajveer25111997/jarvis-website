import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import time
from datetime import datetime

# 1. सुपर-फास्ट रिफ्रेश इंजन (1 सेकंड)
st.set_page_config(page_title="Jarvis Non-Stop Dashboard", layout="wide")
st_autorefresh(interval=1000, key="jarvis_failsafe_engine")

# --- 🛡️ जार्विस "कभी न रुकने वाला" डेटा इंजन (Fail-Safe Logic) ---
def get_data_ultimate(ticker):
    # सोर्स 1: लाइव मार्केट (Yahoo Finance Primary)
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False, timeout=1.5)
        if df is not None and not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df, "🟢 PRIMARY LIVE", "#00FF00"
    except:
        pass # अगर फेल हुआ तो अगले सोर्स पर जाओ
    
    # सोर्स 2: बैकअप सर्वर (Alternative API / Period Change)
    try:
        # यहाँ जार्विस अपना रास्ता बदलता है (5 दिन का डेटा ताकि डेटा मिस न हो)
        df = yf.download(ticker, period="5d", interval="2m", progress=False, timeout=2)
        if df is not None and not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df.tail(60), "🟡 BACKUP SERVER", "#FFFF00"
    except:
        pass

    return None, "🔴 ALL SOURCES OFFLINE", "#FF0000"

# --- 🧠 जार्विस एआई सिग्नल (Call/Put Logic) ---
def jarvis_ai_logic(df):
    if df is None: return "WAIT", 0
    df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
    curr, prev = df.iloc[-1], df.iloc[-2]
    price = curr['Close']
    if curr['E9'] > curr['E21'] and prev['E9'] <= prev['E21']: return "CALL", price
    elif curr['E9'] < curr['E21'] and prev['E9'] >= prev['E21']: return "PUT", price
    return "WAIT", price

# ==========================================
# UI लेआउट शुरू (STATUS BAR)
# ==========================================
st.markdown(f"""
    <div style="background-color: #1e1e1e; padding: 10px; border-radius: 5px; display: flex; justify-content: space-between; border-bottom: 2px solid #444; margin-bottom:10px;">
        <span style="color: #00FF00; font-weight: bold;">🤖 JARVIS CORE: ACTIVE</span>
        <span style="color: #00d4ff;">📡 FAIL-SAFE MODE: ON</span>
        <span style="color: #ffffff;">🕒 {datetime.now().strftime('%H:%M:%S')}</span>
    </div>
    """, unsafe_allow_html=True)

# TOP ROW: इंडेक्स बॉक्स (Metric Boxes)
indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "FIN NIFTY": "NIFTY_FIN_SERVICE.NS"}
cols = st.columns(len(indices))

for i, (name, sym) in enumerate(indices.items()):
    df_i, status, s_color = get_data_ultimate(sym)
    with cols[i]:
        if df_i is not None:
            st.markdown(f'<div style="text-align:center;"><small style="color:{s_color};">{status}</small></div>', unsafe_allow_html=True)
            st.metric(label=name, value=f"₹{df_i['Close'].iloc[-1]:,.1f}")
        else:
            st.metric(label=name, value="RECONNECTING...")

st.divider()

# MAIN SECTION: चार्ट और सिग्नल
data_nifty, status_nifty, color_nifty = get_data_ultimate("^NSEI")
c_main, c_side = st.columns([3, 1])

with c_main:
    if data_nifty is not None:
        fig = go.Figure(data=[go.Candlestick(x=data_nifty.index, open=data_nifty['Open'], high=data_nifty['High'], low=data_nifty['Low'], close=data_nifty['Close'])])
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # ऑप्शन चेन डेटा (सिमुलेशन)
        st.markdown(f"**⛓️ जार्विस ऑप्शन चेन एनालिसिस (LTP: ₹{data_nifty['Close'].iloc[-1]:.2f})**")
        st.caption("🔍 सोर्स: " + status_nifty)

with c_side:
    st.subheader("🎯 एआई सिग्नल्स")
    sig, price = jarvis_ai_logic(data_nifty)
    if sig == "CALL":
        st.success(f"🚀 BUY CALL Zone\nEntry: {price:.2f}\nSL: {price-7:.2f}")
    elif sig == "PUT":
        st.error(f"📉 BUY PUT Zone\nEntry: {price:.2f}\nSL: {price+7:.2f}")
    else:
        st.warning("🔍 नो सिग्नल: जार्विस बाज़ार को स्कैन कर रहा है।")
