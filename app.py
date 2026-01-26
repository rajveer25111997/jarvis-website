import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# 1. पेज सेटअप और सुपर-फास्ट 1s रिफ्रेश
st.set_page_config(page_title="Jarvis RV Ultimate OS", layout="wide")
st_autorefresh(interval=1000, key="jarvis_final_ultimate")

# --- 🛡️ जार्विस डेटा जासूस (Multi-Source Failover) ---
def fetch_data_from_anywhere(ticker):
    # सोर्स 1: Primary Server (1m Interval)
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False, timeout=3)
        if not df.empty and len(df) > 1:
            return df, "🟢 PRIMARY", "#00FF00"
    except: pass

    # सोर्स 2: Backup Server (2m Interval - More Stable)
    try:
        df = yf.download(ticker, period="2d", interval="2m", progress=False, timeout=3)
        if not df.empty:
            return df.tail(60), "🟡 BACKUP", "#FFFF00"
    except: pass

    return None, "🔴 OFFLINE", "#FF0000"

# --- 🔊 वॉइस अलर्ट इंजन ---
def speak(msg):
    st.markdown(f"""<audio autoplay><source src="https://translate.google.com/translate_tts?ie=UTF-8&q={msg}&tl=hi&client=tw-ob" type="audio/mpeg"></audio>""", unsafe_allow_html=True)

# --- 🎯 रिस्क मैनेजमेंट (Quantity Calculator) ---
def get_safe_lots(risk):
    sl_points = 6  # करिश्मा का 6-पॉइंट नियम
    qty = int(risk / sl_points)
    return max(1, qty // 25) # निफ्टी लॉट साइज 25 के हिसाब से

# ==========================================
# 2. STATUS BAR (पट्टी)
# ==========================================
st.markdown(f"""
    <div style="background-color: #1e1e1e; padding: 10px; border-radius: 5px; border-bottom: 2px solid #444; display: flex; justify-content: space-between; align-items: center;">
        <span style="color: #00FF00; font-weight: bold;">🤖 JARVIS RV OS: ACTIVE</span>
        <marquee style="color: #00d4ff; width: 60%;">📢 न्यूज़: ग्लोबल मार्केट पॉजिटिव... बड़े खिलाड़ी निफ्टी में एक्टिव... डेटा इंजन बैकअप मोड में तैनात...</marquee>
        <span style="color: #ffffff;">🕒 {datetime.now().strftime('%H:%M:%S')}</span>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. TOP ROW: इंडेक्स और स्मार्ट डेटा स्टेटस
# ==========================================
indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK"}
cols = st.columns(3)

main_df = None
current_source = ""

for i, (name, sym) in enumerate(indices.items()):
    df, status, s_color = fetch_data_from_anywhere(sym)
    if name == "NIFTY 50": 
        main_df = df
        current_source = status

    if df is not None:
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        price = df['Close'].iloc[-1]
        with cols[i]:
            st.markdown(f"<small style='color:{s_color};'>{status}</small>", unsafe_allow_html=True)
            st.metric(name, f"₹{price:,.1f}")

with cols[2]:
    user_risk = st.number_input("रिस्क बजट (₹):", value=500, step=100)
    rec_lots = get_safe_lots(user_risk)
    st.metric("Suggested Lots", rec_lots)

# ==========================================
# 4. मुख्य चार्ट और व्हेल (Smart Money) ट्रैकर
# ==========================================
st.divider()
if main_df is not None:
    avg_vol = main_df['Volume'].tail(20).mean()
    curr_vol = main_df['Volume'].iloc[-1]
    
    whale_status, whale_color, whale_msg = "⚖️ सामान्य", "#888888", "बाज़ार शांत है"
    if curr_vol > avg_vol * 2.5:
        if main_df['Close'].iloc[-1] > main_df['Open'].iloc[-1]:
            whale_status, whale_color, whale_msg = "🚀 BIG PLAYER ENTRY", "#00FF00", "बड़े खिलाड़ी माल उठा रहे हैं!"
        else:
            whale_status, whale_color, whale_msg = "📉 PANIC EXIT", "#FF4B4B", "सावधान! बड़े प्लेयर्स भाग रहे हैं!"
            speak("राजवीर सर, पैनिक एग्जिट! बड़े खिलाड़ी भाग रहे हैं।")

    st.markdown(f"<div style='border:2px solid {whale_color}; padding:10px; border-radius:10px; text-align:center;'><h3 style='color:{whale_color};'>{whale_status}</h3></div>", unsafe_allow_html=True)

    # चार्ट
    fig = go.Figure(data=[go.Candlestick(x=main_df.index, open=main_df['Open'], high=main_df['High'], low=main_df['Low'], close=main_df['Close'])])
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 5. पेपर ट्रेडिंग लॉग
# ==========================================
st.divider()
st.subheader("📋 आज का ट्रेड लॉग (History)")
if 'log' not in st.session_state: st.session_state.log = []

if st.button("सिम्युलेट ट्रेड (Buy Log)"):
    st.session_state.log.append({"Time": datetime.now().strftime("%H:%M:%S"), "Price": main_df['Close'].iloc[-1], "Lots": rec_lots})
    st.rerun()

if st.session_state.log:
    st.table(pd.DataFrame(st.session_state.log))
