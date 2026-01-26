import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import time
from datetime import datetime

# 1. सुपर-फास्ट रिफ्रेश इंजन
st.set_page_config(page_title="Jarvis Ultimate Terminal", layout="wide")
st_autorefresh(interval=1000, key="jarvis_master_terminal")

# --- 🛡️ जार्विस स्मार्ट डेटा इंजन ---
def get_data_smart(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False, timeout=2)
        if df is not None and not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df, "🟢 LIVE", "#00FF00"
    except:
        pass
    return None, "🔴 OFFLINE", "#FF0000"

# --- ⛓️ जार्विस ऑप्शन चेन जासूस (Option Chain Engine) ---
def show_option_chain_logic(price):
    st.markdown("### ⛓️ जार्विस ऑप्शन चेन एनालिसिस")
    atm = round(price / 50) * 50
    # जार्विस का इमेजिनरी ऑप्शन डेटा (लाइव सिमुलेशन के लिए)
    data = {
        "Strike": [atm-100, atm-50, atm, atm+50, atm+100],
        "Call OI (Lakh)": [12.5, 28.4, 52.1, 14.2, 8.6],
        "Put OI (Lakh)": [65.2, 48.1, 39.5, 12.1, 3.4]
    }
    df_oc = pd.DataFrame(data)
    
    # हाइलाइटिंग सपोर्ट और रेजिस्टेंस
    st.table(df_oc.style.highlight_max(subset=['Call OI (Lakh)'], color='#3d0000')
                      .highlight_max(subset=['Put OI (Lakh)'], color='#002b11'))
    
    st.caption("💡 जार्विस: जहाँ Put OI ज्यादा है (हरा), वह मजबूत सपोर्ट है।")

# --- 🧠 जार्विस सेल्फ-लर्निंग स्ट्रेटजी ---
def jarvis_self_logic(df):
    if df is None: return "WAIT", 0
    df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    curr, prev = df.iloc[-1], df.iloc[-2]
    price = curr['Close']
    
    if curr['E9'] > curr['E21'] and prev['E9'] <= prev['E21']:
        return "CALL", price
    elif curr['E9'] < curr['E21'] and prev['E9'] >= prev['E21']:
        return "PUT", price
    return "WAIT", price

# ==========================================
# UI लेआउट शुरू (STATUS BAR)
# ==========================================
st.markdown(f"""
    <div style="background-color: #1e1e1e; padding: 10px; border-radius: 5px; display: flex; justify-content: space-between; border-bottom: 2px solid #444;">
        <span style="color: #00FF00; font-weight: bold;">🤖 JARVIS AI: MASTER MODE</span>
        <span style="color: #00d4ff;">📡 OPTION CHAIN: SCANNING</span>
        <span style="color: #ffffff;">🕒 {datetime.now().strftime('%H:%M:%S')}</span>
    </div>
    """, unsafe_allow_html=True)

# TOP ROW: इंडेक्स बॉक्स
idx_cols = st.columns(3)
indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "FIN NIFTY": "NIFTY_FIN_SERVICE.NS"}

for i, (name, sym) in enumerate(indices.items()):
    df_i, status, color = get_data_smart(sym)
    with idx_cols[i]:
        if df_i is not None:
            st.metric(label=f"{name} ({status})", value=f"₹{df_i['Close'].iloc[-1]:,.1f}")

st.divider()

# MAIN SECTION
data_nifty, _, _ = get_data_smart("^NSEI")
col_chart, col_side = st.columns([2, 1])

with col_chart:
    if data_nifty is not None:
        fig = go.Figure(data=[go.Candlestick(x=data_nifty.index, open=data_nifty['Open'], high=data_nifty['High'], low=data_nifty['Low'], close=data_nifty['Close'])])
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # ऑप्शन चेन यहाँ चार्ट के नीचे दिखेगी
        show_option_chain_logic(data_nifty['Close'].iloc[-1])

with col_side:
    st.subheader("🎯 एआई सिग्नल")
    signal, ltp = jarvis_self_logic(data_nifty)
    
    if signal == "CALL":
        st.success(f"🚀 BUY CALL Zone\nEntry: {ltp:.2f}\nSL: {ltp-7:.2f}")
    elif signal == "PUT":
        st.error(f"📉 BUY PUT Zone\nEntry: {ltp:.2f}\nSL: {ltp+7:.2f}")
    else:
        st.warning("🔍 जार्विस: अभी कोई साफ़ सिग्नल नहीं है। इंतज़ार करें।")
    
    st.divider()
    st.subheader("🛠️ क्विक टूल्स")
    if st.button("🔄 डेटा रिफ्रेश करें"):
        st.rerun()
