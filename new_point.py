# इसमें आपके सारे पॉइंट्स जमा होंगे
jarvis_skills = {}

# --- पॉइंट 1 (आज का काम) ---
jarvis_skills["market_data"] = "निफ्टी 50 अभी 24,500 पर है।"

# --- पॉइंट 2 (नया विचार) ---
jarvis_skills["trading_strategy"] = "सोमवार को ब्रेकआउट पर नजर रखें।"

# अगर आप गलती से "market_data" दोबारा लिखते हैं, 
# तो ऊपर वाला अपने आप हट जाएगा और नीचे वाला जुड़ जाएगा।
jarvis_skills["market_data"] = "निफ्टी 50 का अपडेटेड डेटा: 24,600"

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# 1. सुपर-फास्ट रिफ्रेश
st.set_page_config(page_title="Jarvis Compact Dashboard", layout="wide")
st_autorefresh(interval=1000, key="jarvis_compact_layout")

# --- 🛡️ स्मार्ट डेटा इंजन (Multi-Source) ---
def get_data_smart(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False, timeout=2)
        if not df.empty:
            return df, "🟢 LIVE", "#00FF00"
    except:
        try:
            df = yf.download(ticker, period="5d", interval="2m", progress=False, timeout=2)
            return df.tail(60), "🟡 BACKUP", "#FFFF00"
        except:
            return None, "🔴 OFFLINE", "#FF0000"

# --- 🔊 वॉइस इंजन ---
def speak_team(msg):
    st.markdown(f"""<audio autoplay><source src="https://translate.google.com/translate_tts?ie=UTF-8&q={msg}&tl=hi&client=tw-ob" type="audio/mpeg"></audio>""", unsafe_allow_html=True)

# ==========================================
# 2. STATUS BAR (सबसे ऊपर की पट्टी)
# ==========================================
st.markdown(f"""
    <div style="background-color: #1e1e1e; padding: 10px; border-radius: 5px; border-bottom: 2px solid #444; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
        <span style="color: #00FF00; font-weight: bold;">🤖 JARVIS SYSTEM: ACTIVE</span>
        <span style="color: #ffffff;">🕒 TIME: {pd.Timestamp.now().strftime('%H:%M:%S')}</span>
        <span style="color: #00d4ff;">🛡️ HEALING: ON</span>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. TOP ROW INDEX (सारे इंडेक्स एक लाइन में)
# ==========================================
indices = {
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "FIN NIFTY": "NIFTY_FIN_SERVICE.NS"
}

# छोटे बॉक्स के लिए Columns
cols = st.columns(len(indices))

for i, (name, sym) in enumerate(indices.items()):
    df_idx, status, s_color = get_data_smart(sym)
    if df_idx is not None:
        if isinstance(df_idx.columns, pd.MultiIndex): df_idx.columns = df_idx.columns.get_level_values(0)
        curr_p = df_idx['Close'].iloc[-1]
        prev_p = df_idx['Close'].iloc[-2]
        change = curr_p - prev_p
        
        with cols[i]:
            # छोटे बॉक्स का स्टाइल
            st.markdown(f"""
                <div style="background-color: #0e1117; padding: 5px; border: 1px solid #444; border-radius: 8px; text-align: center;">
                    <small style="color: {s_color}; font-size: 10px;">{status}</small>
                </div>
            """, unsafe_allow_html=True)
            st.metric(label=name, value=f"₹{curr_p:,.1f}", delta=f"{change:.1f}")

# ==========================================
# 4. MAIN CHART AREA (निफ्टी चार्ट)
# ==========================================
st.divider()
data_nifty, _, _ = get_data_smart("^NSEI")

if data_nifty is not None:
    # 9/21 EMA हीलिंग क्रीम के साथ
    data_nifty['E9'] = data_nifty['Close'].ewm(span=9, adjust=False).mean()
    data_nifty['E21'] = data_nifty['Close'].ewm(span=21, adjust=False).mean()
    
    fig = go.Figure(data=[go.Candlestick(
        x=data_nifty.index, open=data_nifty['Open'], high=data_nifty['High'], 
        low=data_nifty['Low'], close=data_nifty['Close'], name="Price"
    )])
    
    # EMA लाइन्स जोड़ना
    fig.add_trace(go.Scatter(x=data_nifty.index, y=data_nifty['E9'], line=dict(color='orange', width=1), name="EMA 9"))
    fig.add_trace(go.Scatter(x=data_nifty.index, y=data_nifty['E21'], line=dict(color='blue', width=1), name="EMA 21"))
    
    fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

# 5. साइडबार (चैट और सेटिंग्स)
with st.sidebar:
    st.header("💬 जार्विस चैट")
    query = st.text_input("स्टॉक का नाम लिखें...")
    if query:
        st.success(f"जांच कर रहा हूँ: {query}")
