import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import time  # <--- राजवीर सर, टाइम इंजन यहाँ जुड़ गया है
from datetime import datetime

# 1. सुपर-फास्ट रिफ्रेश (1 सेकंड)
st.set_page_config(page_title="Jarvis Time-Sync Dashboard", layout="wide")
st_autorefresh(interval=1000, key="jarvis_final_time_sync")

# --- 🛡️ जार्विस का डेटा जासूस (Time-Check के साथ) ---
def get_data_smart(ticker):
    start_search = time.time() # समय नापना शुरू
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False, timeout=2)
        if df is not None and not df.empty:
            end_search = time.time()
            search_speed = f"{end_search - start_search:.2f}s"
            return df, f"🟢 LIVE ({search_speed})", "#00FF00"
    except:
        pass
    
    try:
        df = yf.download(ticker, period="5d", interval="2m", progress=False, timeout=2)
        if df is not None and not df.empty:
            return df.tail(60), "🟡 BACKUP", "#FFFF00"
    except:
        pass
    return None, "🔴 OFFLINE", "#FF0000"

# --- 🚀 जार्विस सिग्नल बॉक्स (Buy/Sell/Wait) ---
def show_signal_box(df, label):
    if df is not None:
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # इंडिकेटर्स
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        price = df['Close'].iloc[-1]
        e9, e21 = df['E9'].iloc[-1], df['E21'].iloc[-1]
        prev_e9, prev_e21 = df['E9'].iloc[-2], df['E21'].iloc[-2]
        
        # ✅ BUY ZONE
        if e9 > e21 and prev_e9 <= prev_e21:
            sl, tgt = price - 7, price + 15
            st.markdown(f'<div style="background-color:#002b1b; padding:15px; border:2px solid #00ff00; border-radius:10px;">'
                        f'<h3 style="color:#00ff00;margin:0;">🚀 BUY ZONE: {label}</h3>'
                        f'<b>Entry: {price:.2f} | SL: {sl:.2f} | TGT: {tgt:.2f}</b></div>', unsafe_allow_html=True)
        # ❌ SELL ZONE
        elif e9 < e21 and prev_e9 >= prev_e21:
            sl, tgt = price + 7, price - 15
            st.markdown(f'<div style="background-color:#2b0000; padding:15px; border:2px solid #ff4b4b; border-radius:10px;">'
                        f'<h3 style="color:#ff4b4b;margin:0;">📉 SELL ZONE: {label}</h3>'
                        f'<b>Entry: {price:.2f} | SL: {sl:.2f} | TGT: {tgt:.2f}</b></div>', unsafe_allow_html=True)
        # 🟡 WAIT
        else:
            st.warning(f"🟡 WAIT: {label} अभी सुरक्षित जोन में है।")

# ==========================================
# 2. UI लेआउट (STATUS BAR)
# ==========================================
st.markdown(f"""
    <div style="background-color: #1e1e1e; padding: 10px; border-radius: 5px; border-bottom: 2px solid #444; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
        <span style="color: #00FF00; font-weight: bold;">🤖 JARVIS CORE: ONLINE</span>
        <span style="color: #ffffff;">🕒 TIME: {datetime.now().strftime('%H:%M:%S')}</span>
        <span style="color: #00d4ff;">🛡️ HEALING: ACTIVE</span>
    </div>
    """, unsafe_allow_html=True)

# 3. TOP ROW (Index Metrics)
indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "FIN NIFTY": "NIFTY_FIN_SERVICE.NS"}
cols = st.columns(len(indices))

for i, (name, sym) in enumerate(indices.items()):
    idx_df, status, s_color = get_data_smart(sym)
    with cols[i]:
        if idx_df is not None:
            if isinstance(idx_df.columns, pd.MultiIndex): idx_df.columns = idx_df.columns.get_level_values(0)
            st.markdown(f'<div style="text-align:center;"><small style="color:{s_color};">{status}</small></div>', unsafe_allow_html=True)
            st.metric(label=name, value=f"₹{idx_df['Close'].iloc[-1]:,.1f}")

# 4. MAIN DASHBOARD
st.divider()
data_nifty, _, _ = get_data_smart("^NSEI")

col_left, col_right = st.columns([3, 1])

with col_left:
    if data_nifty is not None:
        fig = go.Figure(data=[go.Candlestick(x=data_nifty.index, open=data_nifty['Open'], high=data_nifty['High'], low=data_nifty['Low'], close=data_nifty['Close'])])
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("🎯 सिग्नल ज़ोन")
    show_signal_box(data_nifty, "NIFTY 50")

# 5. SIDEBAR
with st.sidebar:
    st.header("💬 जार्विस असिस्टेंट")
    query = st.text_input("स्टॉक का नाम लिखें:")
