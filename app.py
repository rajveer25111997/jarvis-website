import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. पेज सेटिंग्स और रिफ्रेश पल्स (स्थिरता के लिए 2 सेकंड) ---
st.set_page_config(page_title="JARVIS RV MASTER", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=2000, key="jarvis_final_fix")

# --- 🛡️ 2. डेटा इंजन (Fast & Stable) ---
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
search_query = st.text_input("🔍 Search Stock/Index:", placeholder="यहाँ स्टॉक का नाम लिखें...", key="main_search")

# --- 📊 4. मुख्य इंडेक्स चुनाव ---
indices = {
    "NIFTY 50": {"sym": "^NSEI", "gap": 50},
    "BANK NIFTY": {"sym": "^NSEBANK", "gap": 100},
    "FIN NIFTY": {"sym": "NIFTY_FIN_SERVICE.NS", "gap": 50}
}
selected_idx = st.selectbox("🎯 Select Target Index:", list(indices.keys()), key="idx_select")

# डेटा लोड करना
ticker = indices[selected_idx]["sym"]
gap = indices[selected_idx]["gap"]
df = fetch_market_data(ticker)

# --- 🏗️ 5. लेआउट कंटेनर (यहाँ फिक्स किया गया है) ---
if df is not None and not df.empty:
    ltp = round(df['Close'].iloc[-1], 2)
    atm_strike = round(ltp / gap) * gap

    # ऊपरी हिस्सा: चार्ट और ऑप्शन चैन को एक फिक्स्ड कंटेनर में रखना
    chart_col, oi_col = st.columns([2, 1])
    
    with chart_col:
        # चार्ट को एक खाली जगह (Placeholder) में डालना ताकि वो झपके नहीं
        chart_placeholder = st.empty()
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        chart_placeholder.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with oi_col:
        # ऑप्शन चेन बॉक्स को 'st.markdown' के जरिए स्थिर बनाना
        st.markdown(f"""
            <div style="background:#111; padding:25px; border-radius:15px; border:1px solid #333; height:380px; display:flex; flex-direction:column; justify-content:center; box-sizing: border-box;">
                <p style="color:gray; margin:0; text-align:center;">ATM OPTION CHAIN</p>
                <div style="display:flex; justify-content:space-between; align-items:center; margin:20px 0;">
                    <b style="color:#00ff00; font-size:20px;">CE</b>
                    <span style="color:white; font-size:28px; font-weight:bold;">{atm_strike}</span>
                    <b style="color:#ff4b4b; font-size:20px;">PE</b>
                </div>
                <div style="display:flex; justify-content:space-around;">
                    <span style="color:#00ff00; font-size:22px;">₹ 145.2</span>
                    <span style="color:#ff4b4b; font-size:22px;">₹ 130.8</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # --- 🚨 6. जार्विस सिग्नल बॉक्स (Double होने से रोका गया) ---
    st.write("") # छोटा गैप
    signal_placeholder = st.empty() # सिग्नल के लिए एक ही जगह फिक्स करना
    
    # सिग्नल कैलकुलेशन
    df['E9'] = df['Close'].ewm(span=9).mean()
    df['E21'] = df['Close'].ewm(span=21).mean()
    is_buy = df['E9'].iloc[-1] > df['E21'].iloc[-1]
    sig_text = "BUY (CALL) ACTIVATED" if is_buy else "SELL (PUT) ACTIVATED"
    sig_color = "#00ff00" if is_buy else "#ff4b4b"

    # 'signal_placeholder.markdown' इस्तेमाल करने से बॉक्स डबल नहीं होगा
    signal_placeholder.markdown(f"""
        <div style="background:#07090f; padding:30px; border-radius:20px; border:4px solid {sig_color}; text-align:center; height:180px; display:flex; flex-direction:column; justify-content:center; box-shadow: 0px 0px 15px {sig_color};">
            <h1 style="color:{sig_color}; margin:0; font-size:40px; letter-spacing:2px;">{sig_text}</h1>
            <p style="color:white; font-size:18px; margin-top:10px;">LTP: {ltp} | TGT: {ltp+30} | SL: {ltp-15}</p>
        </div>
    """, unsafe_allow_html=True)

    # --- 🤖 7. AI स्टॉक स्कैनर (सबसे नीचे) ---
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
    st.info("डेटा सिंक किया जा रहा है... कृपया रुकें।")
