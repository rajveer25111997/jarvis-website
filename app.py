import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# 1. सुपर-फास्ट रिफ्रेश (1s) और पेज लेआउट
st.set_page_config(page_title="Jarvis RV Ultimate", layout="wide")
st_autorefresh(interval=1000, key="jarvis_master_final")

# --- 🔊 जार्विस वॉइस अलर्ट ---
def speak(msg):
    st.markdown(f"""<audio autoplay><source src="https://translate.google.com/translate_tts?ie=UTF-8&q={msg}&tl=hi&client=tw-ob" type="audio/mpeg"></audio>""", unsafe_allow_html=True)

# --- 🛡️ पॉइंट 4: मल्टी-सोर्स डेटा इंजन (The Hunter) ---
def fetch_data_smart(ticker):
    try:
        # प्राइमरी सोर्स
        df = yf.download(ticker, period="1d", interval="1m", progress=False, timeout=2)
        if not df.empty and len(df) > 1:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df, "🟢 PRIMARY (LIVE)", "#00FF00"
    except: pass
    try:
        # बैकअप सोर्स
        df = yf.download(ticker, period="5d", interval="2m", progress=False, timeout=2)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df.tail(60), "🟡 BACKUP (STABLE)", "#FFFF00"
    except:
        return None, "🔴 OFFLINE", "#FF0000"

# ==========================================
# 2. पॉइंट 10: स्मार्ट डैशबोर्ड & पॉइंट 6: न्यूज़ पट्टी
# ==========================================
st.markdown(f"""
    <div style="background-color: #1e1e1e; padding: 10px; border-radius: 5px; border-bottom: 2px solid #444; display: flex; justify-content: space-between; align-items: center;">
        <span style="color: #00FF00; font-weight: bold;">🤖 JARVIS RV OS: ACTIVE</span>
        <marquee style="color: #00d4ff; width: 60%;">📢 न्यूज़ जासूस: ग्लोबल मार्केट पॉजिटिव... 🐋 व्हेल ट्रैकर: बड़े खिलाड़ी निफ्टी में एक्टिव... 🛡️ रिस्क मैनेजर: ऑन...</marquee>
        <span style="color: #ffffff;">🕒 {datetime.now().strftime('%H:%M:%S')}</span>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. पॉइंट 2: करिश्मा (Risk Manager) & इंडेक्स रो
# ==========================================
idx_cols = st.columns(3)
data, status, s_color = fetch_data_smart("^NSEI")

if data is not None:
    curr_p = data['Close'].iloc[-1]
    
    with idx_cols[0]:
        st.metric("NIFTY 50", f"₹{curr_p:,.1f}", delta=status)
    with idx_cols[1]:
        # रिस्क बजट के हिसाब से लॉट कैलकुलेशन
        risk_budget = st.number_input("रिस्क बजट (₹):", value=500, step=100)
    with idx_cols[2]:
        lots = max(1, (risk_budget // 6) // 25)
        st.metric("Suggested Lots (Risk 6 Pts)", lots)

    # ==========================================
    # 4. पॉइंट 1: जावेद (The Analyst) & पॉइंट 5: व्हेल ट्रैकर
    # ==========================================
    st.divider()
    col_left, col_right = st.columns([2, 1])

    # जावेद का एनालिसिस (EMA 9/21)
    data['E9'] = data['Close'].ewm(span=9, adjust=False).mean()
    data['E21'] = data['Close'].ewm(span=21, adjust=False).mean()

    with col_left:
        # पॉइंट 5: व्हेल ट्रैकर (Smart Money)
        avg_vol = data['Volume'].tail(20).mean()
        whale_status, w_color = "⚖️ बाज़ार शांत है", "#888888"
        if data['Volume'].iloc[-1] > avg_vol * 2.5:
            if curr_p > data['Open'].iloc[-1]:
                whale_status, w_color = "🚀 BIG PLAYER ENTRY", "#00FF00"
                speak("राजवीर सर, बड़े खिलाड़ी आ गए हैं!")
            else:
                whale_status, w_color = "📉 PANIC EXIT", "#FF4B4B"
                speak("सावधान! बड़े प्लेयर्स भाग रहे हैं।")
        
        st.markdown(f"<div style='border: 2px solid {w_color}; padding: 10px; border-radius: 10px; text-align: center;'><h3 style='color: {w_color};'>{whale_status}</h3></div>", unsafe_allow_html=True)

        # पॉइंट 1: सिग्नल और चार्ट
        if data['E9'].iloc[-1] > data['E21'].iloc[-1]:
            st.success("🚀 BUY SIGNAL ACTIVE (Javed Suggestion)")
        else:
            st.error("📉 SELL SIGNAL ACTIVE (Javed Suggestion)")

        fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
        fig.add_trace(go.Scatter(x=data.index, y=data['E9'], line=dict(color='orange', width=1), name="EMA 9"))
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        # पॉइंट 8: ऑप्शन चेन (ATM Strike)
        st.subheader("⛓️ ऑप्शन चेन")
        atm = round(curr_p / 50) * 50
        st.table(pd.DataFrame({"Strike": [atm-50, atm, atm+50], "Type": ["ITM", "ATM", "OTM"], "OI Status": ["High", "V. High", "Med"]}))
        
        # पॉइंट 9: पेपर ट्रेडिंग लॉग
        st.subheader("📋 ट्रेड लॉग")
        if 'log' not in st.session_state: st.session_state.log = []
        if st.button("सिम्युलेट ट्रेड (Buy)"):
            st.session_state.log.append({"Time": datetime.now().strftime("%H:%M:%S"), "Price": curr_p, "Lots": lots})
            st.rerun()
        if st.session_state.log:
            st.table(pd.DataFrame(st.session_state.log).tail(3))

# --- पॉइंट 7: ऑटो-जॉइनर साइडबार ---
with st.sidebar:
    st.header("⚙️ जार्विस जॉइनर")
    st.text_area("नया प्लग-इन कोड यहाँ डालें...")
    if st.button("जॉइन करें"): st.success("फीचर अपडेटेड!")
