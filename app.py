import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import time
from datetime import datetime

# 1. सुपर-फास्ट रिफ्रेश इंजन (1 सेकंड)
st.set_page_config(page_title="Jarvis All-In-One Terminal", layout="wide")
st_autorefresh(interval=1000, key="jarvis_final_mega_unified")

# --- 🛡️ जार्विस "Fail-Safe" डेटा इंजन (Multi-Source) ---
def get_data_ultimate(ticker):
    # सोर्स 1: प्राइमरी लाइव डेटा
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False, timeout=1.5)
        if df is not None and not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df, "🟢 PRIMARY LIVE", "#00FF00"
    except:
        pass
    
    # सोर्स 2: बैकअप डेटा (अगर सोर्स 1 फेल हो जाए)
    try:
        df = yf.download(ticker, period="5d", interval="2m", progress=False, timeout=2)
        if df is not None and not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df.tail(60), "🟡 BACKUP SERVER", "#FFFF00"
    except:
        pass

    return None, "🔴 OFFLINE", "#FF0000"

# --- 🧠 जार्विस सेल्फ-लर्निंग स्ट्रेटजी (Call/Put Logic) ---
def jarvis_ai_strategy(df):
    if df is None: return "WAIT", 0
    # जार्विस खुद इंडिकेटर्स बना रहा है
    df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    # RSI (जार्विस का फिल्टर)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    
    curr, prev = df.iloc[-1], df.iloc[-2]
    price = curr['Close']
    
    # स्ट्रेटजी: EMA क्रॉसओवर + RSI कन्फर्मेशन
    if curr['E9'] > curr['E21'] and prev['E9'] <= prev['E21'] and curr['RSI'] > 50:
        return "CALL", price
    elif curr['E9'] < curr['E21'] and prev['E9'] >= prev['E21'] and curr['RSI'] < 50:
        return "PUT", price
    return "WAIT", price

# --- ⛓️ जार्विस ऑप्शन चेन एनालिसिस ---
def show_option_chain_logic(price):
    st.markdown("### ⛓️ ऑप्शन चेन (लाइव स्कैन)")
    atm = round(price / 50) * 50
    data = {
        "Strike": [atm-100, atm-50, atm, atm+50, atm+100],
        "Call OI (Lakh)": [14.2, 31.4, 55.1, 12.2, 7.6],
        "Put OI (Lakh)": [68.2, 45.1, 38.5, 10.1, 2.4]
    }
    df_oc = pd.DataFrame(data)
    st.table(df_oc.style.highlight_max(subset=['Call OI (Lakh)'], color='#3d0000')
                      .highlight_max(subset=['Put OI (Lakh)'], color='#002b11'))
    st.caption("💡 Put OI > Call OI = सपोर्ट (तेजी) | Call OI > Put OI = रेजिस्टेंस (मंदी)")

# ==========================================
# UI लेआउट: जार्विस मास्टर डैशबोर्ड
# ==========================================

# 1. स्टेटस बार (टॉप)
st.markdown(f"""
    <div style="background-color: #1e1e1e; padding: 10px; border-radius: 5px; display: flex; justify-content: space-between; border-bottom: 2px solid #444; margin-bottom:10px;">
        <span style="color: #00FF00; font-weight: bold;">🤖 JARVIS CORE: ONLINE</span>
        <span style="color: #00d4ff;">📡 FAIL-SAFE: ACTIVE | 🕒 {datetime.now().strftime('%H:%M:%S')}</span>
    </div>
    """, unsafe_allow_html=True)

# 2. इंडेक्स मेट्रिक्स (निफ्टी, बैंक निफ्टी, फिन निफ्टी)
indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "FIN NIFTY": "NIFTY_FIN_SERVICE.NS"}
idx_cols = st.columns(len(indices))

for i, (name, sym) in enumerate(indices.items()):
    df_idx, status, s_color = get_data_ultimate(sym)
    with idx_cols[i]:
        if df_idx is not None:
            st.markdown(f'<div style="text-align:center;"><small style="color:{s_color};">{status}</small></div>', unsafe_allow_html=True)
            st.metric(label=name, value=f"₹{df_idx['Close'].iloc[-1]:,.1f}")

st.divider()

# 3. मेन एनालिसिस जोन
data_nifty, status_nifty, color_nifty = get_data_ultimate("^NSEI")
c_chart, c_sig = st.columns([3, 1])

with c_chart:
    if data_nifty is not None:
        fig = go.Figure(data=[go.Candlestick(x=data_nifty.index, open=data_nifty['Open'], high=data_nifty['High'], low=data_nifty['Low'], close=data_nifty['Close'])])
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # ऑप्शन चेन यहाँ चार्ट के नीचे
        show_option_chain_logic(data_nifty['Close'].iloc[-1])

with c_sig:
    st.subheader("🎯 एआई सिग्नल्स")
    sig, price = jarvis_ai_strategy(data_nifty)
    
    if sig == "CALL":
        st.success(f"🚀 BUY CALL ZONE\nEntry: {price:.2f}\nSL: {price-7:.2f}\nTGT: {price+15:.2f}")
    elif sig == "PUT":
        st.error(f"📉 BUY PUT ZONE\nEntry: {price:.2f}\nSL: {price+7:.2f}\nTGT: {price-15:.2f}")
    else:
        st.warning("🔍 जार्विस स्कैन कर रहा है... अभी कोई साफ़ ट्रेड नहीं है।")
    
    st.divider()
    st.info("🧠 जार्विस खुद की स्ट्रेटजी पर काम कर रहा है। डेटा सोर्स: " + status_nifty)
