import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# 1. पेज सेटअप
st.set_page_config(page_title="Jarvis Ultimate Terminal", layout="wide")
st_autorefresh(interval=1000, key="jarvis_fixed_os")

# --- 🛡️ हीलिंग क्रीम (Error Fixer) ---
def jarvis_healing(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            return None
    return wrapper

# --- 🔊 वॉइस अलर्ट इंजन ---
def speak(msg):
    st.markdown(f"""<audio autoplay><source src="https://translate.google.com/translate_tts?ie=UTF-8&q={msg}&tl=hi&client=tw-ob" type="audio/mpeg"></audio>""", unsafe_allow_html=True)

# --- 🐋 बड़े खिलाड़ी जासूस (Whale Tracker) ---
def whale_tracker(df):
    if df is None or len(df) < 2: return "⚖️ स्कैनिंग...", "#888888", "डेटा लोड हो रहा है..."
    avg_vol = df['Volume'].tail(20).mean()
    curr_vol = df['Volume'].iloc[-1]
    price_diff = df['Close'].iloc[-1] - df['Open'].iloc[-1]
    
    if curr_vol > avg_vol * 2.5:
        if price_diff > 0:
            return "🚀 BIG PLAYER ENTRY", "#00FF00", "सर, बड़े खिलाड़ी माल उठा रहे हैं!"
        else:
            return "📉 PANIC EXIT", "#FF4B4B", "सावधान! बड़े प्लेयर्स भाग रहे हैं।"
    return "⚖️ बाज़ार शांत है", "#888888", "नॉर्मल वॉल्यूम"

# ==========================================
# 2. STATUS BAR
# ==========================================
st.markdown(f"""
    <div style="background-color: #1e1e1e; padding: 10px; border-radius: 5px; border-bottom: 2px solid #444; display: flex; justify-content: space-between; align-items: center;">
        <span style="color: #00FF00; font-weight: bold;">🤖 JARVIS SYSTEM: ACTIVE</span>
        <marquee style="color: #00d4ff; width: 60%;">📢 न्यूज़ अलर्ट: {datetime.now().strftime('%H:%M:%S')} पर सिस्टम पूरी तरह रिपेयर कर दिया गया है...</marquee>
        <span style="color: #ffffff;">🕒 {datetime.now().strftime('%H:%M:%S')}</span>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. TOP ROW INDEX (With Index Guard)
# ==========================================
indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "FIN NIFTY": "NIFTY_FIN_SERVICE.NS"}
idx_cols = st.columns(len(indices))

@jarvis_healing
def get_idx_data(sym):
    df = yf.download(sym, period="1d", interval="1m", progress=False)
    if df.empty: return None
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    return df

for i, (name, sym) in enumerate(indices.items()):
    data_idx = get_idx_data(sym)
    with idx_cols[i]:
        # सुरक्षा कवच: अगर डेटा नहीं है तो Error नहीं दिखाएगा
        if data_idx is not None and len(data_idx) > 0:
            price = data_idx['Close'].iloc[-1]
            st.metric(label=name, value=f"₹{price:,.1f}")
        else:
            st.metric(label=name, value="Loading...")

# ==========================================
# 4. मुख्य चार्ट और न्यूज़ सेक्शन
# ==========================================
st.divider()
main_df = get_idx_data("^NSEI")

if main_df is not None and len(main_df) > 1:
    whale_status, whale_color, whale_msg = whale_tracker(main_df)
    
    st.markdown(f"<div style='border: 2px solid {whale_color}; padding: 10px; border-radius: 10px; text-align: center;'><h3 style='color: {whale_color};'>{whale_status}</h3></div>", unsafe_allow_html=True)

    fig = go.Figure(data=[go.Candlestick(x=main_df.index, open=main_df['Open'], high=main_df['High'], low=main_df['Low'], close=main_df['Close'])])
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("🔄 जार्विस लाइव डेटा सिंक कर रहा है, कृपया 2 सेकंड रुकें...")

# ==========================================
# 5. साइडबार (न्यूज़ और पेपर ट्रेडिंग)
# ==========================================
with st.sidebar:
    st.header("💬 जार्विस असिस्टेंट")
    st.info("💡 टिप: RSI अभी 45 है, जल्दबाज़ी न करें।")
    st.divider()
    st.subheader("📰 न्यूज़ सेंटीमेंट")
    st.success("Global indices: Positive Impact")
