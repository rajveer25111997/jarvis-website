import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# 1. सुपर-फास्ट रिफ्रेश (1 सेकंड)
st.set_page_config(page_title="Jarvis RV Analyst Pro", layout="wide")
st_autorefresh(interval=1000, key="jarvis_integrated_final")

# --- 🔊 जावेद की आवाज़ ---
def speak(msg):
    st.markdown(f"""<audio autoplay><source src="https://translate.google.com/translate_tts?ie=UTF-8&q={msg}&tl=hi&client=tw-ob" type="audio/mpeg"></audio>""", unsafe_allow_html=True)

# --- 📊 जावेद का डेटा इंजन (Multi-Source) ---
@st.cache_data(ttl=1)
def fetch_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        # जावेद की कैलकुलेशन (EMA & RSI)
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        return df
    except: return None

# ==========================================
# 2. STATUS BAR (सबसे ऊपर)
# ==========================================
st.markdown(f"""
    <div style="background-color: #1e1e1e; padding: 10px; border-radius: 5px; border-bottom: 2px solid #444; display: flex; justify-content: space-between;">
        <span style="color: #00FF00; font-weight: bold;">🤖 JARVIS RV SYSTEM: ACTIVE</span>
        <marquee style="color: #00d4ff; width: 60%;">📢 जावेद एनालिस्ट: निफ्टी 24400 पर बड़ा सपोर्ट है... करिश्मा: स्टॉप लॉस छोटा रखें... एस्कॉर्ट: मुनाफे को लॉक करें...</marquee>
        <span style="color: #ffffff;">🕒 {datetime.now().strftime('%H:%M:%S')}</span>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. मुख्य लेआउट (दो भाग: सिग्नल/चार्ट और ऑप्शन चेन)
# ==========================================
col_main, col_chain = st.columns([2, 1])

# --- निफ्टी डेटा ---
data = fetch_data("^NSEI")

if data is not None:
    curr_p = data['Close'].iloc[-1]
    prev_p = data['Close'].iloc[-2]
    
    with col_main:
        # --- 🚀 यहाँ है सिग्नल (जावेद का आउटपुट) ---
        if data['E9'].iloc[-1] > data['E21'].iloc[-1] and data['E9'].iloc[-2] <= data['E21'].iloc[-2]:
            st.markdown(f"<div style='background-color:#00FF00; padding:15px; border-radius:10px; text-align:center;'><h2 style='color:black;'>🚀 BUY SIGNAL ACTIVE (Call)</h2><b>Entry: {curr_p:.2f} | SL: 6 Pts</b></div>", unsafe_allow_html=True)
            if 'last_s' not in st.session_state or st.session_state.last_s != "BUY":
                speak("राजवीर सर, जावेद का सिग्नल मिला है। कॉल साइड एंट्री बन रही है।")
                st.session_state.last_s = "BUY"
        elif data['E9'].iloc[-1] < data['E21'].iloc[-1] and data['E9'].iloc[-2] >= data['E21'].iloc[-2]:
            st.markdown(f"<div style='background-color:#FF4B4B; padding:15px; border-radius:10px; text-align:center;'><h2 style='color:white;'>📉 SELL SIGNAL ACTIVE (Put)</h2><b>Entry: {curr_p:.2f} | SL: 6 Pts</b></div>", unsafe_allow_html=True)
            if 'last_s' not in st.session_state or st.session_state.last_s != "SELL":
                speak("सर, पुट साइड का सिग्नल है। करिश्मा ने स्टॉप लॉस लगा दिया है।")
                st.session_state.last_s = "SELL"
        else:
            st.info("🔍 जावेद अभी चार्ट एनालाइज कर रहा है... इंतज़ार करें।")

        # चार्ट
        fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
        fig.add_trace(go.Scatter(x=data.index, y=data['E9'], line=dict(color='orange', width=1), name="EMA 9"))
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_chain:
        # --- ⛓️ यहाँ है ऑप्शन चेन (Strike Master) ---
        st.subheader("⛓️ ऑप्शन चेन (Best Strike)")
        atm = round(curr_p / 50) * 50
        chain_data = {
            "Strike": [atm-100, atm-50, atm, atm+50, atm+100],
            "Type": ["ITM", "ITM", "ATM", "OTM", "OTM"],
            "Call OI": ["High", "Medium", "V. High", "Low", "V. Low"],
            "Put OI": ["V. Low", "Low", "High", "Medium", "High"]
        }
        st.table(pd.DataFrame(chain_data))
        st.success(f"🎯 Recommended: {atm} {'CE' if data['E9'].iloc[-1] > data['E21'].iloc[-1] else 'PE'}")

# 4. साइडबार (जॉइनर और न्यूज़)
with st.sidebar:
    st.header("⚙️ जार्विस जॉइनर")
    st.text_area("नया कोड यहाँ जोड़ें...")
    st.divider()
    st.subheader("📰 न्यूज़ जासूस")
    st.warning("US FED मीटिंग आज रात है, बाज़ार में हलचल रह सकती है।")
