import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import base64

# 1. सुपर-फास्ट रिफ्रेश (1 सेकंड)
st.set_page_config(page_title="Jarvis Ultimate AI", layout="wide")
st_autorefresh(interval=1000, key="jarvis_final_terminal")

# --- वॉइस इंजन (जावेद और करिश्मा की आवाज़) ---
def speak_team(msg):
    audio_html = f"""<audio autoplay><source src="https://translate.google.com/translate_tts?ie=UTF-8&q={msg}&tl=hi&client=tw-ob" type="audio/mpeg"></audio>"""
    st.markdown(audio_html, unsafe_allow_html=True)

# --- स्ट्राइक प्राइस मास्टर ---
def get_strike(price, side):
    base = 50
    strike = round(price / base) * base
    return f"{strike} {'CE' if side == 'CALL' else 'PE'}"

# --- डेटा लोडर इंजन ---
@st.cache_data(ttl=1)
def fetch_live_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        return df
    except: return None

# --- साइडबार: जार्विस चैट बॉक्स और मॉर्निंग रिसर्च ---
with st.sidebar:
    st.header("🤖 जार्विस कंट्रोल सेंटर")
    
    # मॉर्निंग रिसर्च
    if st.button("आज का Battle Plan"):
        speak_team("राजवीर सर, आज के ग्लोबल संकेत बुलिश हैं। सावधानी से ट्रेड करें।")
        st.info("🎯 आज का व्यू: निफ्टी में 24500 के ऊपर बड़ा ब्रेकआउट संभव है।")
    
    st.divider()
    
    # "Ask Jarvis" चैट बॉक्स
    st.subheader("💬 जार्विस से पूछें")
    user_query = st.text_input("किसी स्टॉक का नाम लिखें (उदा: RVNL):", placeholder="यहाँ टाइप करें...")
    
    if user_query:
        ticker_query = user_query.upper()
        if not ticker_query.endswith(".NS"): ticker_query += ".NS"
        try:
            q_stock = yf.Ticker(ticker_query)
            q_price = q_stock.history(period="1d")['Close'].iloc[-1]
            st.success(f"🤖 जार्विस: {ticker_query} अभी ₹{q_price:.2f} पर है।")
            speak_team(f"राजवीर सर, {user_query} का भाव अभी {q_price:.0f} रुपये है।")
        except:
            st.error("🤖 जार्विस: सर, स्टॉक का नाम सही लिखें।")

# --- मुख्य डैशबोर्ड ---
st.title("🤖 JARVIS MEGA TERMINAL : Team RV")

col1, col2 = st.columns(2)

def run_trading_engine(ticker, label, column):
    df = fetch_live_data(ticker)
    if df is not None:
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        price = curr['Close']
        
        with column:
            # --- एनालिसिस और मिनिमम लॉस सिग्नल ---
            if curr['E9'] > curr['E21'] and prev['E9'] <= prev['E21']:
                strike = get_strike(price, "CALL")
                sl, tgt = price - 6, price + 15 # करिश्मा का मिनिमम रिस्क लॉजिक
                
                st.markdown(f"<div style='border:3px solid #00FF00; padding:15px; border-radius:15px; background-color: #0e1117;'>"
                            f"<h2 style='color:#00FF00;'>🚀 CALL SIGNAL: {strike}</h2>"
                            f"<b>Entry: {price:.2f} | 🛑 SL: {sl:.2f} | 🎯 Target: {tgt:.2f}</b><br>"
                            f"<small>🛡️ एस्कॉर्ट: मुनाफे को ट्रेल करने के लिए तैनात!</small></div>", unsafe_allow_html=True)
                
                if 'alert' not in st.session_state or st.session_state.alert != f"{ticker}_CALL":
                    speak_team(f"राजवीर सर, {label} में {strike} की कॉल लीजिए। सिर्फ 6 पॉइंट का स्टॉप लॉस है।")
                    st.session_state.alert = f"{ticker}_CALL"

            elif curr['E9'] < curr['E21'] and prev['E9'] >= prev['E21']:
                strike = get_strike(price, "PUT")
                sl, tgt = price + 6, price - 15
                st.markdown(f"<div style='border:3px solid #FF4B4B; padding:15px; border-radius:15px; background-color: #0e1117;'>"
                            f"<h2 style='color:#FF4B4B;'>📉 PUT SIGNAL: {strike}</h2>"
                            f"<b>Entry: {price:.2f} | 🛑 SL: {sl:.2f} | 🎯 Target: {tgt:.2f}</b></div>", unsafe_allow_html=True)
                
                if 'alert' not in st.session_state or st.session_state.alert != f"{ticker}_PUT":
                    speak_team(f"सर, {label} में {strike} का पुट बन रहा है। रिस्क कम है।")
                    st.session_state.alert = f"{ticker}_PUT"

            st.metric(f"Live {label}", f"₹{price:,.2f}")
            
            # चार्ट (Professional View)
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.add_trace(go.Scatter(x=df.index, y=df['E9'], name="EMA9", line=dict(color='orange', width=1)))
            fig.add_trace(go.Scatter(x=df.index, y=df['E21'], name="EMA21", line=dict(color='blue', width=1)))
            fig.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)

# जार्विस इंजन चालू करें
run_trading_engine("^NSEI", "NIFTY 50", col1)
run_trading_engine("^NSEBANK", "BANK NIFTY", col2)

st.divider()
st.caption("💡 राजवीर सर, जार्विस 24/7 लाइव है। स्क्रीन बंद होने पर भी आवाज़ आती रहेगी।")
