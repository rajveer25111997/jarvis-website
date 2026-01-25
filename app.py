import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import base64

# सेटअप
st.set_page_config(page_title="Jarvis & Karishma: Safe Trade", layout="wide")
st_autorefresh(interval=3000, key="jarvis_karishma_tick")

def speak_text(text):
    audio_html = f"""<audio autoplay><source src="https://translate.google.com/translate_tts?ie=UTF-8&q={text}&tl=hi&client=tw-ob" type="audio/mpeg"></audio>"""
    st.markdown(audio_html, unsafe_allow_html=True)

# --- करिश्मा का रिस्क मैनेजमेंट इंजन ---
def get_safe_exit(entry_price, signal_type):
    # निफ्टी के लिए 1:2 का रिस्क रिवॉर्ड रेशियो
    if signal_type == "CALL":
        sl = entry_price - 7  # 7 पॉइंट का स्टॉप लॉस
        target = entry_price + 15 # 15 पॉइंट का टारगेट
    else:
        sl = entry_price + 7
        target = entry_price - 15
    return sl, target

st.title("🤖 JARVIS & 👩‍🔬 KARISHMA : Entry-Exit Duo")

index_choice = st.sidebar.selectbox("इंडेक्स चुनें:", ["^NSEI", "^NSEBANK"])
data = yf.download(index_choice, period="1d", interval="1m", progress=False)

if not data.empty:
    if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
    data['EMA9'] = data['Close'].ewm(span=9, adjust=False).mean()
    data['EMA21'] = data['Close'].ewm(span=21, adjust=False).mean()
    
    curr = data.iloc[-1]
    prev = data.iloc[-2]
    entry_p = float(curr['Close'])
    
    # --- जार्विस और करिश्मा की जुगलबंदी ---
    status = "इंतज़ार करें"
    status_color = "white"
    
    if curr['EMA9'] > curr['EMA21'] and prev['EMA9'] <= prev['EMA21']:
        sl, tgt = get_safe_exit(entry_p, "CALL")
        status = "🚀 CALL SIGNAL (Jarvis Entry)"
        status_color = "#00FF00"
        speak_text(f"राजवीर सर, जार्विस ने कॉल दिया है। करिश्मा कह रही है कि स्टॉप लॉस {sl:.0f} पर लगाएं और {tgt:.0f} पर प्रॉफिट बुक करें")
        st.sidebar.success(f"📍 SL: {sl:.2f} | TGT: {tgt:.2f}")

    elif curr['EMA9'] < curr['EMA21'] and prev['EMA9'] >= prev['EMA21']:
        sl, tgt = get_safe_exit(entry_p, "PUT")
        status = "📉 PUT SIGNAL (Jarvis Entry)"
        status_color = "#FF4B4B"
        speak_text(f"सर, पुट का सिग्नल है। करिश्मा की सलाह है कि स्टॉप लॉस {sl:.0f} रखें और {tgt:.0f} पर एग्जिट करें")
        st.sidebar.error(f"📍 SL: {sl:.2f} | TGT: {tgt:.2f}")

    # मेन डिस्प्ले
    st.markdown(f"""
        <div style='background-color: {status_color}22; border: 3px solid {status_color}; padding: 20px; border-radius: 15px; text-align: center;'>
            <h1 style='color: {status_color};'>{status}</h1>
            <h3>Price: {entry_p:,.2f}</h3>
        </div>
    """, unsafe_allow_html=True)

    # चार्ट पर SL और TGT लाइनें
    fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
    if status != "इंतज़ार करें":
        fig.add_hline(y=sl, line_dash="dot", line_color="orange", annotation_text="Karishma StopLoss")
        fig.add_hline(y=tgt, line_dash="dot", line_color="cyan", annotation_text="Jarvis Target")
    
    fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
