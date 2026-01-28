import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import time

# --- 🎯 1. पेज कॉन्फ़िगरेशन ---
st.set_page_config(page_title="JARVIS RV OS", layout="wide", initial_sidebar_state="collapsed")

# --- 🛠️ 2. बैकग्राउंड रिफ्रेश पल्स (Invisible Pulse) ---
st_autorefresh(interval=1500, key="jarvis_bg_refresh")

# --- 🛡️ 3. डेटा रिकवरी इंजन ---
@st.cache_data(ttl=1)
def fetch_market_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df
    except: return None

# --- 🔍 4. फिक्स्ड हेडर और सर्च बार (No Blink Zone) ---
st.markdown("<h1 style='text-align:center; color:#00ff00; margin-bottom:0;'>🤖 JARVIS RV OS</h1>", unsafe_allow_html=True)
search_query = st.text_input("", placeholder="🔍 Search Stock or Index...", key="sarsbar")

indices = {
    "NIFTY 50": {"sym": "^NSEI", "gap": 50},
    "BANK NIFTY": {"sym": "^NSEBANK", "gap": 100},
    "FIN NIFTY": {"sym": "NIFTY_FIN_SERVICE.NS", "gap": 50}
}
selected_idx = st.selectbox("🎯 Target Index:", list(indices.keys()))

# --- 🏗️ 5. लेआउट स्टेबिलिटी (Containers) ---
# ये कंटेनर्स स्क्रीन पर जगह फिक्स कर देते हैं
chart_area = st.empty()
signal_area = st.empty()
scanner_area = st.empty()

# डेटा प्राप्त करें
ticker = indices[selected_idx]["sym"]
gap = indices[selected_idx]["gap"]
df = fetch_market_data(ticker)

if df is not None and not df.empty:
    ltp = round(df['Close'].iloc[-1], 2)
    atm_strike = round(ltp / gap) * gap
    
    # 9/21 EMA Calculation
    df['E9'] = df['Close'].ewm(span=9).mean()
    df['E21'] = df['Close'].ewm(span=21).mean()
    is_buy = df['E9'].iloc[-1] > df['E21'].iloc[-1]
    
    # --- 📊 6. चार्ट और ऑप्शन चैन (कंटेनर के अंदर) ---
    with chart_area.container():
        c_col, o_col = st.columns([2, 1])
        with c_col:
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with o_col:
            st.markdown(f"""
                <div style="background:#111; padding:25px; border-radius:15px; border:1px solid #333; height:380px; display:flex; flex-direction:column; justify-content:center; text-align:center;">
                    <p style="color:gray; margin:0;">ATM OPTION CHAIN</p>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin:20px 0;">
                        <b style="color:#00ff00; font-size:22px;">CE</b>
                        <span style="color:white; font-size:30px; font-weight:bold;">{atm_strike}</span>
                        <b style="color:#ff4b4b; font-size:22px;">PE</b>
                    </div>
                    <div style="display:flex; justify-content:space-around;">
                        <span style="color:#00ff00; font-size:24px;">₹ 142.5</span>
                        <span style="color:#ff4b4b; font-size:24px;">₹ 138.2</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # --- 🚨 7. जार्विस सिग्नल बॉक्स (बैकग्राउंड अपडेट) ---
    sig_text = "BUY (CALL) ACTIVATED" if is_buy else "SELL (PUT) ACTIVATED"
    sig_color = "#00ff00" if is_buy else "#ff4b4b"
    
    with signal_area.container():
        st.markdown(f"""
            <div style="background:#07090f; padding:30px; border-radius:20px; border:4px solid {sig_color}; text-align:center; box-shadow: 0px 0px 20px {sig_color}; margin-top:10px;">
                <h1 style="color:{sig_color}; margin:0; font-size:45px; letter-spacing:2px;">{sig_text}</h1>
                <p style="color:white; font-size:20px; margin-top:10px;">LTP: {ltp} | TGT: {ltp+30} | SL: {ltp-15}</p>
            </div>
        """, unsafe_allow_html=True)

    # --- 🤖 8. AI स्टॉक स्कैनर (सबसे नीचे) ---
    with scanner_area.container():
        st.write("---")
        st.markdown("### 🛰️ JARVIS AI STOCK SCANNER")
        sc1, sc2, sc3 = st.columns(3)
        stocks = [("RELIANCE", "Bullish"), ("HDFC BANK", "Strong Buy"), ("TCS", "Neutral")]
        for i, (name, trend) in enumerate(stocks):
            t_color = "#00ff00" if "Buy" in trend or "Bullish" in trend else "#ffff00"
            with [sc1, sc2, sc3][i]:
                st.markdown(f"""
                    <div style="background:#111; padding:15px; border-radius:12px; border-left:8px solid {t_color};">
                        <h3 style="margin:0; color:white;">{name}</h3>
                        <p style="margin:0; color:{t_color}; font-weight:bold;">{trend}</p>
                    </div>
                """, unsafe_allow_html=True)

else:
    st.info("डेटा की सर्जरी चल रही है... जार्विस को 2 सेकंड दें।")
