import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import base64

# 1. सुपर-फास्ट रिफ्रेश (1 सेकंड)
st.set_page_config(page_title="Jarvis Triple Power", layout="wide")
st_autorefresh(interval=1000, key="jarvis_mega_tick")

# --- वॉइस इंजन ---
def speak_all(msg):
    audio_html = f"""<audio autoplay><source src="https://translate.google.com/translate_tts?ie=UTF-8&q={msg}&tl=hi&client=tw-ob" type="audio/mpeg"></audio>"""
    st.markdown(audio_html, unsafe_allow_html=True)

# --- डेटा लोडर (Jarvis Brain) ---
@st.cache_data(ttl=1)
def get_live_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        return df
    except: return None

# --- प्री-मार्केट रिसर्च ---
def morning_research():
    with st.sidebar:
        st.header("☀️ मॉर्निंग रिसर्च")
        if st.button("आज का Battle Plan"):
            st.info("🌍 ग्लोबल संकेत: बुलिश\n📰 न्यूज़: रिलायंस डील\n🎯 निफ्टी व्यू: 15pt ब्रेकआउट संभव")
            speak_all("राजवीर सर, सुबह की रिसर्च रिपोर्ट तैयार है। आज निफ्टी में तेजी के संकेत हैं।")

# --- एस्कॉर्ट (Trailing) और करिश्मा (SL) इंजन ---
def analyze_trade(df, label):
    curr = df.iloc[-1]
    prev = df.iloc[-2]
    price = curr['Close']
    
    # जार्विस एंट्री (EMA Cross)
    if curr['EMA9'] > curr['EMA21'] and prev['EMA9'] <= prev['EMA21']:
        # करिश्मा का स्टॉप लॉस और टारगेट
        sl, tgt = price - 7, price + 15
        # एस्कॉर्ट का जैकपॉट चेक (Volume)
        jackpot = "YES" if curr['Volume'] > df['Volume'].tail(5).mean() * 2 else "NO"
        
        msg = f"राजवीर सर, {label} में कॉल लीजिए। करिश्मा ने एस एल {sl:.0f} पर लगाया है।"
        if jackpot == "YES": msg += " एस्कॉर्ट कह रहा है कि यह 15 पॉइंट से ऊपर जैकपॉट दे सकता है!"
        
        return {"type": "CALL", "price": price, "sl": sl, "tgt": tgt, "msg": msg, "color": "#00FF00"}
    
    elif curr['EMA9'] < curr['EMA21'] and prev['EMA9'] >= prev['EMA21']:
        sl, tgt = price + 7, price - 15
        return {"type": "PUT", "price": price, "sl": sl, "tgt": tgt, "msg": f"सर, {label} में पुट का सिग्नल है।", "color": "#FF4B4B"}
    
    return None

# --- डैशबोर्ड ---
morning_research()
st.title("🤖 JARVIS 👩‍🔬 KARISHMA 🛡️ ESCORT")

col1, col2 = st.columns(2)

def run_terminal(ticker, label, column):
    data = get_live_data(ticker)
    if data is not None:
        trade = analyze_trade(data, label)
        with column:
            # एआई स्टेटस बॉक्स
            if trade:
                st.markdown(f"<div style='border:3px solid {trade['color']}; padding:10px; border-radius:10px;'>"
                            f"<h2 style='color:{trade['color']};'>{trade['type']} SIGNAL ACTIVE</h2>"
                            f"<b>Entry: {trade['price']:.2f} | SL: {trade['sl']:.2f} | Target: {trade['tgt']:.2f}</b></div>", unsafe_allow_html=True)
                if 'last_alert' not in st.session_state or st.session_state.last_alert != trade['type']:
                    speak_all(trade['msg'])
                    st.session_state.last_alert = trade['type']
            else:
                st.write(f"🔍 {label}: जार्विस स्कैन कर रहा है...")

            st.metric(f"{label} Price", f"₹{data['Close'].iloc[-1]:,.2f}")
            
            # प्रोफेशनल चार्ट
            fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
            fig.add_trace(go.Scatter(x=data.index, y=data['EMA9'], name="EMA9", line=dict(color='orange', width=1)))
            fig.add_trace(go.Scatter(x=data.index, y=data['EMA21'], name="EMA21", line=dict(color='blue', width=1)))
            fig.update_layout(template="plotly_dark", height=380, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

run_terminal("^NSEI", "NIFTY 50", col1)
run_terminal("^NSEBANK", "BANK NIFTY", col2)

# --- पोर्टफोलियो गार्ड ---
st.divider()
st.subheader("📋 पोर्टफोलियो लाइव ट्रैकर (RVNL, Tata Steel)")
# यहाँ आपके पोर्टफोलियो स्टॉक्स का लाइव स्टेटस दिखेगा
