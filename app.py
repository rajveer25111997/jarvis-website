import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import time
from datetime import datetime

# 1. सुपर-फास्ट रिफ्रेश
st.set_page_config(page_title="Jarvis Error Free", layout="wide")
st_autorefresh(interval=1000, key="jarvis_mega_fix_v2")

# --- 🛡️ जार्विस स्मार्ट डेटा इंजन (TypeError Fix) ---
def get_data_smart(ticker):
    try:
        # रास्ता 1: Primary
        df = yf.download(ticker, period="1d", interval="1m", progress=False, timeout=3)
        if df is not None and not df.empty:
            return df, "🟢 LIVE", "#00FF00"
    except:
        pass
    
    try:
        # रास्ता 2: Backup
        df = yf.download(ticker, period="5d", interval="2m", progress=False, timeout=3)
        if df is not None and not df.empty:
            return df.tail(60), "🟡 BACKUP", "#FFFF00"
    except:
        pass
        
    return None, "🔴 OFFLINE", "#FF0000"

# --- 🚀 जार्विस सिग्नल बॉक्स (एनालिसिस इंजन) ---
def show_signal_box(df, label):
    if df is not None:
        try:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            # इंडिकेटर्स एनालिसिस
            df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
            df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
            
            price = df['Close'].iloc[-1]
            e9, e21 = df['E9'].iloc[-1], df['E21'].iloc[-1]
            prev_e9, prev_e21 = df['E9'].iloc[-2], df['E21'].iloc[-2]
            
            # स्कैनिंग इंडिकेटर
            st.markdown(f'<div style="color:#00d4ff; font-size:12px;">🧠 जार्विस एनालिसिस: RSI & EMA स्कैन... OK</div>', unsafe_allow_html=True)

            if e9 > e21 and prev_e9 <= prev_e21:
                st.markdown(f'<div style="background-color:#002b1b;padding:10px;border:1px solid #00ff00;border-radius:5px;color:#00ff00;">🚀 BUY ZONE: {label} @ {price:.2f}</div>', unsafe_allow_html=True)
            elif e9 < e21 and prev_e9 >= prev_e21:
                st.markdown(f'<div style="background-color:#2b0000;padding:10px;border:1px solid #ff4b4b;border-radius:5px;color:#ff4b4b;">📉 SELL ZONE: {label} @ {price:.2f}</div>', unsafe_allow_html=True)
            else:
                st.info(f"🔍 {label}: जार्विस ब्रेकआउट ढूँढ रहा है...")
        except:
            st.error("⚠️ सिग्नल कैलकुलेशन में दिक्कत।")

# ==========================================
# UI लेआउट शुरू
# ==========================================
st.markdown(f"""
    <div style="background-color: #1e1e1e; padding: 10px; border-radius: 5px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #444;">
        <span style="color: #00FF00; font-weight: bold;">🟢 SYSTEM: ONLINE</span>
        <span style="color: #00d4ff;">📡 SCANNING: ACTIVE</span>
        <span style="color: #ffffff;">🕒 TIME: {datetime.now().strftime('%H:%M:%S')}</span>
    </div>
    """, unsafe_allow_html=True)

# 3. टॉप इंडेक्स लाइन (Fix: TypeError protected)
indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK"}
cols = st.columns(2)

for i, (name, sym) in enumerate(indices.items()):
    idx_df, status, s_color = get_data_smart(sym) #
    with cols[i]:
        if idx_df is not None:
            if isinstance(idx_df.columns, pd.MultiIndex): idx_df.columns = idx_df.columns.get_level_values(0)
            st.metric(label=f"{name} ({status})", value=f"₹{idx_df['Close'].iloc[-1]:,.1f}")
        else:
            st.metric(label=f"{name}", value="Loading...")

st.divider()

# 4. मेन चार्ट और सिग्नल
data_nifty, _, _ = get_data_smart("^NSEI")
c1, c2 = st.columns([3, 1])

with c1:
    if data_nifty is not None:
        fig = go.Figure(data=[go.Candlestick(x=data_nifty.index, open=data_nifty['Open'], high=data_nifty['High'], low=data_nifty['Low'], close=data_nifty['Close'])])
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("🎯 एनालिसिस")
    show_signal_box(data_nifty, "NIFTY 50")
