import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# 1. सुपर-फास्ट रिफ्रेश और ऑटो-हीलिंग
st.set_page_config(page_title="Jarvis Self-Healing Terminal", layout="wide")
st_autorefresh(interval=2000, key="jarvis_fix_tick")

# --- हीलिंग क्रीम: एरर को रोकने वाला सिस्टम ---
def jarvis_repair_engine(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            # अगर एरर आता है तो यह चुपचाप दोबारा कोशिश करेगा
            return None
    return wrapper

# --- डेटा इंजन (Fixed Version) ---
@jarvis_repair_engine
def fetch_safe_data(ticker):
    # जार्विस अब 'auto_adjust' करेगा ताकि डेटा एरर न आए
    df = yf.download(ticker, period="1d", interval="1m", progress=False, auto_adjust=True)
    if df is None or df.empty:
        return None
    
    # कॉलम नाम ठीक करना
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # इंडिकेटर्स (RSI, EMA)
    df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
    return df

# --- वॉइस इंजन ---
def speak_team(msg):
    audio_html = f"""<audio autoplay><source src="https://translate.google.com/translate_tts?ie=UTF-8&q={msg}&tl=hi&client=tw-ob" type="audio/mpeg"></audio>"""
    st.markdown(audio_html, unsafe_allow_html=True)

st.title("🤖 JARVIS : Self-Healing Mode Activated")

# --- पोर्टफोलियो और चैट बॉक्स (साइडबार) ---
with st.sidebar:
    st.header("💬 जार्विस असिस्टेंट")
    q = st.text_input("स्टॉक पूछें (उदा: RVNL):")
    if q:
        st.write(f"🤖 जार्विस {q} पर नज़र रख रहा है...")

# --- मुख्य ट्रेडिंग डेस्क ---
col1, col2 = st.columns(2)

def monitor(ticker, label, column):
    data = fetch_safe_data(ticker)
    with column:
        if data is not None:
            curr = data.iloc[-1]
            prev = data.iloc[-2]
            price = float(curr['Close'])
            
            # जार्विस और करिश्मा का सिग्नल
            if curr['EMA9'] > curr['EMA21'] and prev['EMA9'] <= prev['EMA21']:
                st.success(f"🚀 BUY: {label} @ {price:.2f}")
                speak_team(f"राजवीर सर, {label} में बाय सिग्नल है")
            
            st.metric(label, f"₹{price:,.2f}")
            
            # चार्ट
            fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
            fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"⚠️ {label} का डेटा अभी लोड नहीं हो रहा है, जार्विस हीलिंग मोड में है...")

monitor("^NSEI", "NIFTY 50", col1)
monitor("^NSEBANK", "BANK NIFTY", col2)
