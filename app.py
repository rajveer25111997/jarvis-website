import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import base64

# सेटअप
st.set_page_config(page_title="Jarvis Portfolio Guard", layout="wide")
st_autorefresh(interval=5000, key="jarvis_portfolio_tick")

def speak_text(text):
    audio_html = f"""<audio autoplay><source src="https://translate.google.com/translate_tts?ie=UTF-8&q={text}&tl=hi&client=tw-ob" type="audio/mpeg"></audio>"""
    st.markdown(audio_html, unsafe_allow_html=True)

# --- आपके पोर्टफोलियो की लिस्ट (यहाँ आप नए नाम जोड़ सकते हैं) ---
my_portfolio = ["RVNL.NS", "TATASTEEL.NS", "RELIANCE.NS", "IRFC.NS"]

st.title("🤖 JARVIS : My Portfolio Watchdog")

# पोर्टफोलियो समरी
st.subheader("📋 आपके स्टॉक्स पर जार्विस की नज़र")
p_cols = st.columns(len(my_portfolio))

for i, ticker in enumerate(my_portfolio):
    stock_data = yf.download(ticker, period="1d", interval="1m", progress=False)
    
    if not stock_data.empty:
        curr_p = stock_data['Close'].iloc[-1]
        prev_p = stock_data['Open'].iloc[0]
        p_change = ((curr_p - prev_p) / prev_p) * 100
        
        with p_cols[i]:
            # डिज़ाइनर कार्ड
            color = "green" if p_change >= 0 else "red"
            st.markdown(f"""
                <div style='border: 2px solid {color}; padding: 10px; border-radius: 10px; text-align: center;'>
                    <h4 style='margin:0;'>{ticker.split('.')[0]}</h4>
                    <h2 style='margin:0; color:{color};'>₹{curr_p:,.2f}</h2>
                    <p style='margin:0; color:{color};'>{p_change:.2f}%</p>
                </div>
            """, unsafe_allow_html=True)
            
            # जार्विस का क्रिटिकल अलर्ट (अगर 3% से ज्यादा हलचल हो)
            if abs(p_change) > 3.0:
                st.warning(f"⚠️ {ticker} में बड़ी हलचल!")
                speak_text(f"राजवीर सर, आपके पोर्टफोलियो स्टॉक {ticker} में भारी उतार चढ़ाव हो रहा है")

st.divider()

# --- पोर्टफोलियो एनालिसिस इंजन ---
st.subheader("🔍 जार्विस एनालिसिस: आज क्या बेचें, क्या रखें?")
for t in my_portfolio:
    df = yf.download(t, period="5d", interval="15m", progress=False)
    if not df.empty:
        # 9/21 EMA चेक
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        last_c = df['Close'].iloc[-1]
        e9 = df['E9'].iloc[-1]
        
        if last_c > e9:
            st.write(f"✅ **{t}:** होल्ड रखें, स्टॉक मजबूत दिख रहा है।")
        else:
            st.write(f"❌ **{t}:** कमजोरी के संकेत हैं, स्टॉप-लॉस का ध्यान रखें।")
