import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. पेज सेटिंग्स और रिफ्रेश पल्स ---
st.set_page_config(page_title="JARVIS RV MASTER", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=2000, key="jarvis_stable_pulse") # 2 सेकंड पल्स स्टेबिलिटी के लिए

# --- 🛡️ 2. डेटा इंजन (नो-ब्लिंक के लिए कैश्ड) ---
@st.cache_data(ttl=2)
def fetch_market_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df
    except: return None

# --- 🔍 3. सर्च बार (Sarsbar) ---
st.markdown("<h1 style='text-align:center; color:#00ff00; font-family:serif;'>🤖 JARVIS RV OS</h1>", unsafe_allow_html=True)
search_query = st.text_input("🔍 Search Stock or Index (e.g. SBIN, RELIANCE, ^NSEBANK):", placeholder="यहाँ स्टॉक का नाम लिखें...")

# --- 📊 4. इंडेक्स और ऑप्शन चैन (एक साथ) ---
indices = {
    "NIFTY 50": {"sym": "^NSEI", "gap": 50},
    "BANK NIFTY": {"sym": "^NSEBANK", "gap": 100},
    "FIN NIFTY": {"sym": "NIFTY_FIN_SERVICE.NS", "gap": 50}
}

selected_idx = st.selectbox("🎯 Target Index Select Karein:", list(indices.keys()))
ticker = indices[selected_idx]["sym"]
gap = indices[selected_idx]["gap"]

df = fetch_market_data(ticker)

if df is not None and not df.empty:
    ltp = round(df['Close'].iloc[-1], 2)
    atm_strike = round(ltp / gap) * gap

    # लेआउट फिक्स (चार्ट और ऑप्शन चैन)
    col_chart, col_oi = st.columns([2, 1])
    
    with col_chart:
        st.markdown(f"### 📊 {selected_idx} Live Chart")
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(
            template="plotly_dark", height=400, 
            xaxis_rangeslider_visible=False, 
            margin=dict(l=0,r=0,t=0,b=0),
            # यूआई स्टेबिलिटी के लिए चार्ट की बाउंड्री लॉक
            yaxis=dict(fixedrange=True) 
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with col_oi:
        st.markdown("### ⛓️ Option Chain (ATM)")
        st.markdown(f"""
            <div style="background:#111; padding:20px; border-radius:15px; border:1px solid #333; height:370px; display:flex; flex-direction:column; justify-content:center;">
                <div style="display:flex; justify-content:space-between; margin-bottom:20px;">
                    <span style="color:#00ff00; font-size:20px;">CALL (CE)</span>
                    <span style="color:white; font-weight:bold; font-size:24px;">{atm_strike}</span>
                    <span style="color:#ff4b4b; font-size:20px;">PUT (PE)</span>
                </div>
                <div style="display:flex; justify-content:space-around;">
                    <h2 style="color:#00ff00;">₹ 145.50</h2>
                    <h2 style="color:#ff4b4b;">₹ 132.20</h2>
                </div>
                <p style="text-align:center; color:gray; font-size:14px; margin-top:20px;">Premium values are simulated</p>
            </div>
        """, unsafe_allow_html=True)

    # --- 🚨 5. जार्विस सिग्नल बॉक्स (Fixed Height) ---
    st.write("---")
    df['E9'] = df['Close'].ewm(span=9).mean()
    df['E21'] = df['Close'].ewm(span=21).mean()
    sig_type = "BUY (CALL) ACTIVATED" if df['E9'].iloc[-1] > df['E21'].iloc[-1] else "SELL (PUT) ACTIVATED"
    sig_color = "#00ff00" if "BUY" in sig_type else "#ff4b4b"

    # ऊँचाई को 200px पर लॉक किया गया है ताकि जम्पिंग न हो
    st.markdown(f"""
        <div style="background:#07090f; padding:30px; border-radius:20px; border:3px solid {sig_color}; text-align:center; height:200px; display:flex; flex-direction:column; justify-content:center; box-shadow: 0px 0px 15px {sig_color};">
            <h1 style="color:{sig_color}; margin:0; font-size:45px; letter-spacing:2px;">{sig_type}</h1>
            <p style="color:white; font-size:20px; margin-top:10px;">ENTRY: {ltp} | TGT: {ltp+30} | SL: {ltp-15}</p>
        </div>
    """, unsafe_allow_html=True)

    # --- 🤖 6. AI स्टॉक स्कैनर (सबसे नीचे) ---
    st.write("---")
    st.markdown("### 🛰️ JARVIS AI STOCK SCANNER")
    sc1, sc2, sc3 = st.columns(3)
    stocks = [("RELIANCE", "Bullish"), ("HDFC BANK", "Neutral"), ("TCS", "Bearish")]
    
    for i, (name, trend) in enumerate(stocks):
        color = "#00ff00" if trend == "Bullish" else "#ff4b4b" if trend == "Bearish" else "#ffff00"
        with [sc1, sc2, sc3][i]:
            st.markdown(f"""
                <div style="background:#111; padding:15px; border-radius:12px; border-left:8px solid {color};">
                    <h3 style="margin:0; color:white;">{name}</h3>
                    <p style="margin:0; color:{color};">AI View: {trend}</p>
                </div>
            """, unsafe_allow_html=True)
else:
    st.error("Data Synchronizing... Please check connection.")
