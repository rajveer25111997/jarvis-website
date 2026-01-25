import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import base64

# 1. पेज सेटअप
st.set_page_config(page_title="Jarvis Master Terminal", layout="wide", initial_sidebar_state="expanded")

# 2. याददाश्त (Session State) सेट करना
if 'my_portfolio' not in st.session_state:
    st.session_state.my_portfolio = ["RVNL.NS", "TATASTEEL.NS", "RELIANCE.NS"]

# 3. 1 सेकंड का रिफ्रेश
st_autorefresh(interval=1000, key="jarvis_final_sync")

# वॉइस फंक्शन
def speak_text(text):
    audio_html = f"""<audio autoplay><source src="https://translate.google.com/translate_tts?ie=UTF-8&q={text}&tl=hi&client=tw-ob" type="audio/mpeg"></audio>"""
    st.markdown(audio_html, unsafe_allow_html=True)

# --- साइडबार: पोर्टफोलियो मैनेजर ---
st.sidebar.title("🛠️ जार्विस कंट्रोल")

# A. स्टॉक जोड़ना
st.sidebar.subheader("➕ नया स्टॉक")
new_s = st.sidebar.text_input("NSE सिंबल (e.g. SBIN.NS):")
if st.sidebar.button("लिस्ट में जोड़ें"):
    if new_s:
        clean_s = new_s.upper().strip()
        if clean_s not in st.session_state.my_portfolio:
            st.session_state.my_portfolio.append(clean_s)
            st.sidebar.success(f"{clean_s} एडेड!")
            st.rerun()

st.sidebar.divider()

# B. स्टॉक हटाना (Indentation Fixed)
st.sidebar.subheader("🗑️ स्टॉक हटाएँ")
if len(st.session_state.my_portfolio) > 0:
    to_del = st.sidebar.selectbox("चुनें:", st.session_state.my_portfolio)
    if st.sidebar.button("डिलीट करें"):
        st.session_state.my_portfolio.remove(to_del)
        st.sidebar.error(f"{to_del} डिलीटेड!")
        st.rerun()
else:
    st.sidebar.info("लिस्ट खाली है।")

# --- मुख्य स्क्रीन: लाइव फीड ---
st.title("🤖 JARVIS : Live Portfolio & Market")

# 4. टॉप स्टॉक्स (ग्रिड व्यू)
if st.session_state.my_portfolio:
    p_cols = st.columns(len(st.session_state.my_portfolio))
    for i, ticker in enumerate(st.session_state.my_portfolio):
        try:
            data = yf.download(ticker, period="1d", interval="1m", progress=False)
            if not data.empty:
                cp = float(data['Close'].iloc[-1])
                op = float(data['Open'].iloc[0])
                ch = ((cp - op) / op) * 100
                clr = "green" if ch >= 0 else "red"
                
                with p_cols[i]:
                    st.markdown(f"""
                        <div style='border: 2px solid {clr}; padding: 10px; border-radius: 10px; text-align: center; background-color: #0d1117;'>
                            <h4 style='margin:0; color: white;'>{ticker.split('.')[0]}</h4>
                            <h2 style='margin:0; color:{clr}; font-size: 22px;'>₹{cp:,.2f}</h2>
                            <p style='margin:0; color:{clr}; font-weight: bold;'>{ch:.2f}%</p>
                        </div>
                    """, unsafe_allow_html=True)
        except:
            continue

st.divider()

# 5. लाइव इंडेक्स चार्ट्स (Nifty & Bank Nifty)
c1, c2 = st.columns(2)
def draw_idx(t, lbl, col):
    d = yf.download(t, period="1d", interval="1m", progress=False)
    with col:
        if not d.empty:
            st.subheader(f"📊 {lbl}")
            fig = go.Figure(data=[go.Candlestick(x=d.index, open=d['Open'], high=d['High'], low=d['Low'], close=d['Close'])])
            fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

draw_idx("^NSEI", "NIFTY 50", c1)
draw_idx("^NSEBANK", "BANK NIFTY", c2)

# जावेद वॉइस एक्टिवेशन
if st.sidebar.button("जावेद को बुलाओ 🔊"):
    speak_text("नमस्ते राजवीर सर, आपका पोर्टफोलियो और मार्केट लाइव है")
