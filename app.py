import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import base64

# 1. सुपर-फ़ास्ट 3s रिफ्रेश और डार्क थीम
st.set_page_config(page_title="Jarvis Super AI", layout="wide")
st_autorefresh(interval=3000, key="jarvis_super_refresh")

# --- वॉइस फंक्शन ---
def speak_text(text):
    audio_html = f"""<audio autoplay><source src="https://translate.google.com/translate_tts?ie=UTF-8&q={text}&tl=hi&client=tw-ob" type="audio/mpeg"></audio>"""
    st.markdown(audio_html, unsafe_allow_html=True)

# --- कैंडलस्टिक पैटर्न डिटेक्टर (पॉइंट 2) ---
def detect_patterns(df):
    patterns = []
    if len(df) < 2: return ""
    last = df.iloc[-1]
    body = abs(last['Close'] - last['Open'])
    wick_h = last['High'] - max(last['Open'], last['Close'])
    wick_l = min(last['Open'], last['Close']) - last['Low']
    
    if wick_l > (body * 2): patterns.append("🔨 Hammer (Bullish)")
    if wick_h > (body * 2): patterns.append("🏹 Shooting Star (Bearish)")
    if body < ( (last['High'] - last['Low']) * 0.1): patterns.append("⚖️ Doji (Confusion)")
    return ", ".join(patterns) if patterns else "Scanning..."

# --- स्मार्ट डेटा हंटर ---
@st.cache_data(ttl=2)
def get_jarvis_data(ticker, interval):
    try:
        df = yf.download(ticker, period="2d", interval=interval, progress=False)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        return df
    except: return None

# --- UI Layout ---
st.title("🤖 JARVIS : Advanced AI Terminal")

# न्यूज़ टिकर (पॉइंट 5)
st.markdown("<marquee style='color: #FF4B4B; font-weight: bold;'>⚠️ अलर्ट: जार्विस लाइव मार्केट स्कैन कर रहा है... | निफ्टी रेजिस्टेंस: 24,500 | बिटकॉइन सपोर्ट: $88,000</marquee>", unsafe_allow_html=True)

# साइडबार कंट्रोल्स
st.sidebar.header("🕹️ Control Panel")
timeframe = st.sidebar.selectbox("टाइमफ्रेम चुनें (पॉइंट 7):", ["1m", "5m", "15m", "1h"], index=0)
if st.sidebar.button("जावेद को बुलाओ 🎤"):
    speak_text("स्वागत है राजवीर सर, जार्विस के सुपर एआई मोड में आपका स्वागत है")

col1, col2 = st.columns(2)

# मार्केट प्रोसेसिंग
def process_advanced_market(ticker, label, col):
    data = get_jarvis_data(ticker, timeframe)
    with col:
        if data is not None and len(data) > 5:
            # पैटर्न और सिग्नल
            pattern = detect_patterns(data)
            e9, e21 = data['EMA9'].iloc[-1], data['EMA21'].iloc[-1]
            
            # विजुअल कार्ड्स
            c1, c2 = st.columns(2)
            c1.metric(f"{label} Price", f"{data['Close'].iloc[-1]:,.2f}")
            c2.info(f"पैटर्न: {pattern}")
            
            # चार्ट
            fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
            fig.add_trace(go.Scatter(x=data.index, y=data['EMA9'], name="9 EMA", line=dict(color='orange')))
            fig.add_trace(go.Scatter(x=data.index, y=data['EMA21'], name="21 EMA", line=dict(color='blue')))
            fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)
            
            # वॉइस अलर्ट लॉजिक
            if e9 > e21 and data['EMA9'].iloc[-2] <= data['EMA21'].iloc[-2]:
                speak_text(f"सर, {label} में खरीदारी का सिग्नल मिला है और {pattern} भी दिख रहा है")

process_advanced_market("^NSEI", "NIFTY 50", col1)
process_advanced_market("BTC-USD", "BITCOIN", col2)
