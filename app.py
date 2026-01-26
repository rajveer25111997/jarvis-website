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

import new_point

def run_jarvis_web():
    print("--- जार्विस वेबसाइट शुरू हो रही है ---")
    
    # यह लूप अपने आप सारे पॉइंट्स को एक-एक करके दिखाएगा
    # अगर कोई डुप्लीकेट होगा, तो डिक्शनरी उसे पहले ही साफ कर चुकी होगी
    for skill_name, detail in new_point.jarvis_skills.items():
        print(f"पॉइंट का नाम: {skill_name}")
        print(f"विवरण: {detail}")
        print("-" * 20)

# --- जार्विस सिग्नल बॉक्स इंजन (सिर्फ कोड) ---

show_signal_box(data_nifty, "NIFTY 50")

def show_signal_box(df, label):
    if df is not None:
        # 9/21 EMA लॉजिक
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        price = curr['Close']
        
        # 1. बुलिश सिग्नल (CALL)
        if curr['E9'] > curr['E21'] and prev['E9'] <= prev['E21']:
            sl = price - 7  # करिश्मा का 7 पॉइंट SL
            tgt = price + 15 # जार्विस का 15 पॉइंट टारगेट
            
            st.markdown(f"""
                <div style="background-color: #002b1b; padding: 15px; border: 2px solid #00ff00; border-radius: 10px; margin-bottom: 10px;">
                    <h3 style="color: #00ff00; margin: 0;">🚀 {label} - BUY SIGNAL</h3>
                    <p style="margin: 5px 0;"><b>Entry:</b> {price:.2f} | <b>SL:</b> {sl:.2f} | <b>Target:</b> {tgt:.2f}</p>
                    <small style="color: #00ff00;">🛡️ एस्कॉर्ट: मुनाफे को ट्रेल करने के लिए तैयार!</small>
                </div>
            """, unsafe_allow_html=True)
            
        # 2. बीयरिश सिग्नल (PUT)
        elif curr['E9'] < curr['E21'] and prev['E9'] >= prev['E21']:
            sl = price + 7
            tgt = price - 15
            
            st.markdown(f"""
                <div style="background-color: #2b0000; padding: 15px; border: 2px solid #ff4b4b; border-radius: 10px; margin-bottom: 10px;">
                    <h3 style="color: #ff4b4b; margin: 0;">📉 {label} - SELL SIGNAL</h3>
                    <p style="margin: 5px 0;"><b>Entry:</b> {price:.2f} | <b>SL:</b> {sl:.2f} | <b>Target:</b> {tgt:.2f}</p>
                    <small style="color: #ff4b4b;">🛡️ करिश्मा: रिस्क कंट्रोल में है।</small>
                </div>
            """, unsafe_allow_html=True)
        
        # 3. कोई सिग्नल नहीं
        else:
            st.info(f"🔍 {label}: जार्विस ब्रेकआउट ढूँढ रहा है...")

if __name__ == "__main__":
    run_jarvis_web()
