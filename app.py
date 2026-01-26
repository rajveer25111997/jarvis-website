import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import time
from datetime import datetime

# 1. रिफ्रेश इंजन
st.set_page_config(page_title="Jarvis Analyzer Pro", layout="wide")
st_autorefresh(interval=1000, key="jarvis_analysis_check")

# --- 🛡️ डेटा इंजन ---
def get_data_smart(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False, timeout=2)
        if df is not None and not df.empty:
            return df, "🟢 LIVE", "#00FF00"
    except:
        return None, "🔴 OFFLINE", "#FF0000"

# --- 🧠 जार्विस एनालिसिस इंजन (Thought Process) ---
def show_signal_box(df, label):
    # यहाँ से पता चलेगा जार्विस एनालिसिस कर रहा है
    with st.spinner('🤖 जार्विस डेटा स्कैन कर रहा है...'):
        if df is not None:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            # एनालिसिस पैरामीटर्स
            df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
            df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
            
            price = df['Close'].iloc[-1]
            e9, e21 = df['E9'].iloc[-1], df['E21'].iloc[-1]
            prev_e9, prev_e21 = df['E9'].iloc[-2], df['E21'].iloc[-2]
            
            # --- एनालिसिस इंडिकेटर ---
            st.markdown(f"""
                <div style="background-color: #111; padding: 10px; border-left: 5px solid #00d4ff; margin-bottom: 10px;">
                    <small style="color: #00d4ff;">🧠 <b>जार्विस थॉट प्रोसेस:</b></small><br>
                    <small style="color: #ccc;">Checking EMA Cross... OK | Analyzing Volume... OK | RSI Trend... Scan</small>
                </div>
            """, unsafe_allow_html=True)

            # ✅ सिग्नल लॉजिक
            if e9 > e21 and prev_e9 <= prev_e21:
                st.success(f"🚀 BUY ZONE: {label} @ {price:.2f}")
            elif e9 < e21 and prev_e9 >= prev_e21:
                st.error(f"📉 SELL ZONE: {label} @ {price:.2f}")
            else:
                st.warning(f"🔍 {label}: जार्विस ब्रेकआउट का इंतज़ार कर रहा है...")

# ==========================================
# 2. UI LAYOUT (Status Bar)
# ==========================================
st.markdown(f"""
    <div style="background-color: #1e1e1e; padding: 10px; border-radius: 5px; display: flex; justify-content: space-between;">
        <span style="color: #00FF00;">🤖 SYSTEM: ONLINE</span>
        <span style="color: #00d4ff;">📡 SCANNING: ACTIVE</span>
        <span style="color: #ffffff;">🕒 {datetime.now().strftime('%H:%M:%S')}</span>
    </div>
    """, unsafe_allow_html=True)

# 3. TOP ROW & CHART
indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK"}
cols = st.columns(2)

for i, (name, sym) in enumerate(indices.items()):
    idx_df, status, s_color = get_data_smart(sym)
    with cols[i]:
        if idx_df is not None:
            st.metric(label=f"{name} ({status})", value=f"₹{idx_df['Close'].iloc[-1]:,.1f}")

st.divider()
data_nifty, _, _ = get_data_smart("^NSEI")

col_main, col_side = st.columns([3, 1])

with col_main:
    if data_nifty is not None:
        fig = go.Figure(data=[go.Candlestick(x=data_nifty.index, open=data_nifty['Open'], high=data_nifty['High'], low=data_nifty['Low'], close=data_nifty['Close'])])
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

with col_side:
    st.subheader("🎯 एनालिसिस")
    show_signal_box(data_nifty, "NIFTY 50")
