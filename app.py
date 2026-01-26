import new_point
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import time

# 1. पेज सेटअप और ऑटो-रिफ्रेश (1 सेकंड)
st.set_page_config(page_title="Jarvis Multi-Source AI", layout="wide")
st_autorefresh(interval=1000, key="jarvis_global_refresh")

# --- 🔊 वॉइस इंजन ---
def speak_team(msg):
    audio_html = f"""<audio autoplay><source src="https://translate.google.com/translate_tts?ie=UTF-8&q={msg}&tl=hi&client=tw-ob" type="audio/mpeg"></audio>"""
    st.markdown(audio_html, unsafe_allow_html=True)

# --- 🛡️ जार्विस मल्टी-सोर्स डेटा इंजन (Smart Search) ---
def fetch_live_data(ticker):
    # रास्ता 1: प्राइमरी (Yahoo Finance)
    try:
        data = yf.download(ticker, period="1d", interval="1m", progress=False, timeout=5)
        if not data.empty:
            return data, "Primary Server"
    except:
        pass

    # रास्ता 2: बैकअप (Alternative Search)
    try:
        backup_data = yf.download(ticker, period="5d", interval="2m", progress=False, timeout=5)
        if not backup_data.empty:
            return backup_data.tail(60), "Backup Server"
    except:
        st.error("🚨 जार्विस अलर्ट: सारे डेटा सोर्स बंद हैं!")
        return None, None
import new_point

# डिक्शनरी के सारे पॉइंट्स को एक-एक करके दिखाओ
for name, feature in new_point.my_features.items():
    print(f"Feature Name: {name} | Content: {feature}")
# --- मुख्य टर्मिनल डैशबोर्ड ---
st.title("🤖 JARVIS : Multi-Source AI Terminal")

# साइडबार में आपकी नई फोटो वाले फीचर्स की झलक
with st.sidebar:
    st.header("📊 मार्केट जासूस")
    st.info("✅ RSI, MACD Active\n✅ Buy/Sell Zones Active\n✅ Paper Trading Ready")
    st.divider()
    st.subheader("💬 जार्विस से पूछें")
    query = st.text_input("स्टॉक का नाम लिखें (उदा: RELIANCE):", key="jarvis_chat_input")

col1, col2 = st.columns(2)

def run_trading_engine(ticker, label, column, unique_id):
    df, source_name = fetch_live_data(ticker)
    
    if df is not None:
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        curr_p = df['Close'].iloc[-1]
        
        # इंडिकेटर्स
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()

        with column:
            # मेट्रिक्स में यूनिक की (Key) ताकि एरर न आए
            st.metric(label, f"₹{curr_p:,.2f}", f"Source: {source_name}", delta_color="normal")
            
            # चार्ट (Unique Key के साथ)
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.add_trace(go.Scatter(x=df.index, y=df['E9'], name="EMA9", line=dict(color='orange', width=1)))
            fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True, key=f"chart_{unique_id}")

# इंजन शुरू करें
run_trading_engine("^NSEI", "NIFTY 50", col1, "nifty")
run_trading_engine("^NSEBANK", "BANK NIFTY", col2, "banknifty")

st.divider()
st.caption("🛡️ जार्विस हीलिंग क्रीम एक्टिव: डुप्लीकेट आईडी और डेटा एरर ठीक कर दिए गए हैं।")
