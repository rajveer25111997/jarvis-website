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
import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. पेज सेटअप और याददाश्त (Memory) सेट करना
if 'my_portfolio' not in st.session_state:
    # ये आपके शुरुआती स्टॉक्स हैं
    st.session_state.my_portfolio = ["RVNL.NS", "TATASTEEL.NS", "RELIANCE.NS"]

st_autorefresh(interval=3000, key="jarvis_sync")

# --- साइडबार: स्टॉक मैनेजमेंट ---
st.sidebar.title("🛠️ जार्विस कंट्रोल सेंटर")

# A. नया स्टॉक जोड़ने का तरीका
st.sidebar.subheader("➕ स्टॉक जोड़ें")
new_stock = st.sidebar.text_input("NSE सिंबल डालें (जैसे: SBIN.NS):")
if st.sidebar.button("पोर्टफोलियो में डालें"):
    if new_stock:
        clean_stock = new_stock.upper().strip()
        if clean_stock not in st.session_state.my_portfolio:
            st.session_state.my_portfolio.append(clean_stock)
            st.sidebar.success(f"{clean_stock} जोड़ दिया गया!")
            st.rerun()
        else:
            st.sidebar.warning("यह स्टॉक पहले से लिस्ट में है।")

st.sidebar.divider()

# B. स्टॉक हटाने (Delete) का तरीका
st.sidebar.subheader("🗑️ स्टॉक हटाएँ")
if st.session_state.my_portfolio:
    stock_to_remove = st.sidebar.selectbox("हटाने के लिए चुनें:", st.session_state.my_portfolio)
    if st.sidebar.button("लिस्ट से डिलीट करें"):
        st.session_state.my_portfolio.remove(stock_to_remove)
        st.sidebar.error(f"{stock_to_remove} हटा दिया गया!")
        st.rerun()
else:
    st.sidebar.write("लिस्ट खाली है।")

# --- मुख्य स्क्रीन पर डिस्प्ले ---
st.title("🤖 JARVIS : Live Portfolio Guard")

if not st.session_state.my_portfolio:
    st.info("आपका पोर्टफोलियो खाली है। साइडबार से स्टॉक जोड़ें।")
else:
    # स्टॉक्स को सुंदर ग्रिड में दिखाना
    cols = st.columns(len(st.session_state.my_portfolio))
    
    for i, ticker in enumerate(st.session_state.my_portfolio):
        try:
            data = yf.download(ticker, period="1d", interval="1m", progress=False)
            if not data.empty:
                curr_p = float(data['Close'].iloc[-1])
                prev_p = float(data['Open'].iloc[0])
                change = ((curr_p - prev_p) / prev_p) * 100
                color = "green" if change >= 0 else "red"
                
                with cols[i]:
                    st.markdown(f"""
                        <div style='border: 2px solid {color}; padding: 10px; border-radius: 10px; text-align: center; background-color: #0d1117;'>
                            <h4 style='margin:0; color: white;'>{ticker.split('.')[0]}</h4>
                            <h2 style='margin:0; color:{color}; font-size: 24px;'>₹{curr_p:,.2f}</h2>
                            <p style='margin:0; color:{color}; font-weight: bold;'>{change:.2f}%</p>
                        </div>
                    """, unsafe_allow_html=True)
        except:
            st.error(f"{ticker} का डेटा नहीं मिला।")            
            st.write(f"❌ **{t}:** कमजोरी के संकेत हैं, स्टॉप-लॉस का ध्यान रखें।")
