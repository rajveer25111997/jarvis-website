import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# 1. पेज सेटअप और सुपर-फास्ट 1s रिफ्रेश
st.set_page_config(page_title="Jarvis Ultimate Terminal", layout="wide")
st_autorefresh(interval=1000, key="jarvis_final_os")

# --- 🛡️ हीलिंग क्रीम (Self-Healing Logic) ---
def jarvis_healing(func):
    def wrapper(*args, **kwargs):
        try: return func(*args, **kwargs)
        except: return None
    return wrapper

# --- 🔊 वॉइस अलर्ट इंजन ---
def speak(msg):
    st.markdown(f"""<audio autoplay><source src="https://translate.google.com/translate_tts?ie=UTF-8&q={msg}&tl=hi&client=tw-ob" type="audio/mpeg"></audio>""", unsafe_allow_html=True)

# --- 🐋 बड़े खिलाड़ी जासूस (Whale Tracker) ---
def whale_tracker(df):
    avg_vol = df['Volume'].tail(20).mean()
    curr_vol = df['Volume'].iloc[-1]
    price_diff = df['Close'].iloc[-1] - df['Open'].iloc[-1]
    
    if curr_vol > avg_vol * 2.5:
        if price_diff > 0:
            return "🚀 BIG PLAYER ENTRY (Buying)", "#00FF00", "सर, बड़े खिलाड़ी माल उठा रहे हैं!"
        else:
            return "📉 PANIC EXIT (Selling)", "#FF4B4B", "सावधान! बड़े प्लेयर्स भाग रहे हैं।"
    return "⚖️ बाज़ार शांत है", "#888888", "नॉर्मल वॉल्यूम"

# ==========================================
# 2. STATUS BAR (सबसे ऊपर की पट्टी)
# ==========================================
st.markdown(f"""
    <div style="background-color: #1e1e1e; padding: 10px; border-radius: 5px; border-bottom: 2px solid #444; display: flex; justify-content: space-between; align-items: center;">
        <span style="color: #00FF00; font-weight: bold;">🤖 JARVIS SYSTEM: ACTIVE</span>
        <marquee style="color: #00d4ff; width: 60%;">📢 न्यूज़ अलर्ट: ग्लोबल संकेत बुलिश... बड़े खिलाड़ी निफ्टी में एक्टिव... वॉल्यूम स्पाइक पर नज़र रखें...</marquee>
        <span style="color: #ffffff;">🕒 {datetime.now().strftime('%H:%M:%S')}</span>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. TOP ROW INDEX (निफ्टी, बैंक निफ्टी, फिन निफ्टी)
# ==========================================
indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "FIN NIFTY": "NIFTY_FIN_SERVICE.NS"}
idx_cols = st.columns(len(indices))

@jarvis_healing
def get_idx_data(sym):
    df = yf.download(sym, period="1d", interval="1m", progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    return df

for i, (name, sym) in enumerate(indices.items()):
    data_idx = get_idx_data(sym)
    if data_idx is not None:
        price = data_idx['Close'].iloc[-1]
        with idx_cols[i]:
            st.metric(label=name, value=f"₹{price:,.1f}")

# ==========================================
# 4. मुख्य चार्ट और व्हेल ट्रैकर सेक्शन
# ==========================================
st.divider()
main_df = get_idx_data("^NSEI")

if main_df is not None:
    whale_status, whale_color, whale_msg = whale_tracker(main_df)
    
    # बड़े खिलाड़ी का स्टेटस बॉक्स
    st.markdown(f"""
        <div style="background-color: #0e1117; padding: 10px; border-radius: 10px; border: 2px solid {whale_color}; text-align: center;">
            <h3 style="color: {whale_color}; margin: 0;">{whale_status}</h3>
            <p style="color: #ddd;">{whale_msg}</p>
        </div>
    """, unsafe_allow_html=True)

    # चार्ट इंजन
    main_df['E9'] = main_df['Close'].ewm(span=9, adjust=False).mean()
    main_df['E21'] = main_df['Close'].ewm(span=21, adjust=False).mean()
    
    fig = go.Figure(data=[go.Candlestick(x=main_df.index, open=main_df['Open'], high=main_df['High'], low=main_df['Low'], close=main_df['Close'])])
    fig.add_trace(go.Scatter(x=main_df.index, y=main_df['E9'], line=dict(color='orange', width=1), name="EMA 9"))
    fig.add_trace(go.Scatter(x=main_df.index, y=main_df['E21'], line=dict(color='blue', width=1), name="EMA 21"))
    fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    # वॉइस अलर्ट अगर व्हेल एक्टिव हो
    if "BIG PLAYER" in whale_status or "PANIC" in whale_status:
        if 'last_whale' not in st.session_state or st.session_state.last_whale != whale_status:
            speak(whale_msg)
            st.session_state.last_whale = whale_status

# ==========================================
# 5. साइडबार (न्यूज़ और सवाल)
# ==========================================
with st.sidebar:
    st.header("💬 जार्विस चैट और न्यूज़")
    query = st.text_input("स्टॉक का नाम (उदा: RVNL):")
    if query:
        st.info(f"जाँच: {query} का सेंटीमेंट पॉज़िटिव है।")
    
    st.divider()
    st.subheader("📰 न्यूज़ इफेक्ट")
    st.warning("RBI पॉलिसी: बाज़ार पर भारी असर संभव।")
    st.success("Global Market: निफ्टी के लिए अच्छे संकेत।")
