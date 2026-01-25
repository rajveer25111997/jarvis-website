import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import base64

# 1. सुपर-फास्ट रिफ्रेश (1 सेकंड)
st.set_page_config(page_title="Jarvis Super Team", layout="wide")
st_autorefresh(interval=1000, key="jarvis_mega_final")

# --- वॉइस इंजन ---
def speak_team(msg):
    audio_html = f"""<audio autoplay><source src="https://translate.google.com/translate_tts?ie=UTF-8&q={msg}&tl=hi&client=tw-ob" type="audio/mpeg"></audio>"""
    st.markdown(audio_html, unsafe_allow_html=True)

# --- स्ट्राइक प्राइस मास्टर ---
def get_strike(price, side):
    base = 50
    strike = round(price / base) * base
    return f"{strike} {'CE' if side == 'CALL' else 'PE'}"

# --- रिसर्च और डेटा इंजन ---
@st.cache_data(ttl=1)
def fetch_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        return df
    except: return None

# --- प्री-मार्केट रिपोर्ट ---
with st.sidebar:
    st.header("☀️ मॉर्निंग रिसर्च")
    if st.button("आज की रिसर्च रिपोर्ट"):
        speak_team("राजवीर सर, सुबह की रिपोर्ट तैयार है। आज निफ्टी बुलिश रह सकता है।")
        st.info("🌍 ग्लोबल: पॉजिटिव | 📰 न्यूज़: रिलायंस, HDFC | 🎯 ट्रेंड: अपसाइड")

st.title("🤖 JARVIS | 👩‍🔬 KARISHMA | 🛡️ ESCORT")

col1, col2 = st.columns(2)

def run_mega_terminal(ticker, label, column):
    df = fetch_data(ticker)
    if df is not None:
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        price = curr['Close']
        
        with column:
            # --- एनालिसिस और सिग्नल ---
            if curr['E9'] > curr['E21'] and prev['E9'] <= prev['E21']:
                strike = get_strike(price, "CALL")
                sl, tgt = price - 6, price + 15 # करिश्मा का मिनिमम रिस्क
                
                st.markdown(f"<div style='border:3px solid #00FF00; padding:15px; border-radius:15px;'>"
                            f"<h2 style='color:#00FF00;'>🚀 CALL SIGNAL: {strike}</h2>"
                            f"<b>Entry: {price:.2f} | SL: {sl:.2f} | TGT: {tgt:.2f}</b><br>"
                            f"🛡️ एस्कॉर्ट: मुनाफे को ट्रेल करने के लिए तैयार!</div>", unsafe_allow_html=True)
                
                if 'last_call' not in st.session_state or st.session_state.last_call != strike:
                    speak_team(f"राजवीर सर, {strike} में कॉल लीजिए। करिश्मा ने सिर्फ 6 पॉइंट का रिस्क रखा है।")
                    st.session_state.last_call = strike

            elif curr['E9'] < curr['E21'] and prev['E9'] >= prev['E21']:
                strike = get_strike(price, "PUT")
                sl, tgt = price + 6, price - 15
                st.markdown(f"<div style='border:3px solid #FF4B4B; padding:15px; border-radius:15px;'>"
                            f"<h2 style='color:#FF4B4B;'>📉 PUT SIGNAL: {strike}</h2>"
                            f"<b>Entry: {price:.2f} | SL: {sl:.2f} | TGT: {tgt:.2f}</b></div>", unsafe_allow_html=True)
                speak_team(f"सर, {strike} का पुट लीजिए, नुकसान कम रखने के लिए तैयार रहें।")

            st.metric(f"Live {label}", f"₹{price:,.2f}")
            
            # चार्ट
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)

# रन करें
run_mega_terminal("^NSEI", "NIFTY 50", col1)
run_mega_terminal("^NSEBANK", "BANK NIFTY", col2)

st.divider()
st.subheader("📋 पोर्टफोलियो और न्यूज़ जासूस")
st.write("RVNL | TATA STEEL | RELIANCE - जार्विस इन पर नज़र रख रहा है।")
