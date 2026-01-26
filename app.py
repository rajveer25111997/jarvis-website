import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# 1. सुपर-फास्ट रिफ्रेश और पेज सेटअप
st.set_page_config(page_title="Jarvis RV Analyst Fix", layout="wide")
st_autorefresh(interval=1000, key="jarvis_final_fix")

# --- 🔊 जावेद की आवाज़ ---
def speak(msg):
    st.markdown(f"""<audio autoplay><source src="https://translate.google.com/translate_tts?ie=UTF-8&q={msg}&tl=hi&client=tw-ob" type="audio/mpeg"></audio>""", unsafe_allow_html=True)

# --- 📊 स्मार्ट मल्टी-सोर्स डेटा इंजन (The Fix) ---
def fetch_smart_data(ticker):
    # रास्ता 1: Primary
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False, timeout=2)
        if not df.empty and len(df) > 1:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df, "🟢 LIVE", "#00FF00"
    except: pass
    
    # रास्ता 2: Backup
    try:
        df = yf.download(ticker, period="5d", interval="2m", progress=False, timeout=2)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df.tail(60), "🟡 BACKUP", "#FFFF00"
    except: pass
    
    return None, "🔴 OFFLINE", "#FF0000"

# ==========================================
# 2. STATUS BAR (पट्टी हमेशा रहेगी)
# ==========================================
st.markdown(f"""
    <div style="background-color: #1e1e1e; padding: 10px; border-radius: 5px; border-bottom: 2px solid #444; display: flex; justify-content: space-between;">
        <span style="color: #00FF00; font-weight: bold;">🤖 JARVIS RV SYSTEM: ACTIVE</span>
        <marquee style="color: #00d4ff; width: 60%;">📢 अलर्ट: डेटा सिंक हो रहा है... चार्ट और ऑप्शन चेन नीचे लोड हो रहे हैं... बड़े खिलाड़ी निफ्टी पर नज़र बनाए हुए हैं...</marquee>
        <span style="color: #ffffff;">🕒 {datetime.now().strftime('%H:%M:%S')}</span>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. मुख्य लेआउट (सब कुछ यहाँ वापस आएगा)
# ==========================================
col_main, col_chain = st.columns([2, 1])

data, status, s_color = fetch_smart_data("^NSEI")

if data is not None:
    curr_p = data['Close'].iloc[-1]
    
    # जावेद का एनालिसिस (EMA)
    data['E9'] = data['Close'].ewm(span=9, adjust=False).mean()
    data['E21'] = data['Close'].ewm(span=21, adjust=False).mean()

    with col_main:
        # --- 🚀 सिग्नल ज़ोन ---
        if data['E9'].iloc[-1] > data['E21'].iloc[-1]:
            st.success(f"🚀 BUY ZONE ACTIVE | Price: {curr_p:.2f}")
        else:
            st.error(f"📉 SELL ZONE ACTIVE | Price: {curr_p:.2f}")

        # चार्ट
        fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
        fig.add_trace(go.Scatter(x=data.index, y=data['E9'], line=dict(color='orange', width=1), name="EMA 9"))
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_chain:
        # --- ⛓️ ऑप्शन चेन टेबल ---
        st.subheader("⛓️ ऑप्शन चेन (ATM)")
        atm = round(curr_p / 50) * 50
        chain_df = pd.DataFrame({
            "Strike": [atm-50, atm, atm+50],
            "Type": ["ITM", "ATM", "OTM"],
            "Call OI": ["High", "V. High", "Low"],
            "Put OI": ["Low", "High", "V. High"]
        })
        st.table(chain_df)
        st.info(f"जावेद टिप: {atm} की स्ट्राइक पर ध्यान दें।")
else:
    # अगर डेटा नहीं मिला तो ये दिखेगा
    with col_main:
        st.warning("🔄 राजवीर सर, बाज़ार से डेटा कनेक्ट नहीं हो पा रहा है। जार्विस बैकअप सोर्स ढूँढ रहा है...")
    with col_chain:
        st.info("डेटा लोड होते ही ऑप्शन चेन यहाँ आ जाएगी।")

# 4. साइडबार
with st.sidebar:
    st.header("⚙️ जार्विस सेटिंग्स")
    st.write(f"Data Source: **{status}**")
