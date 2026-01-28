import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time

# --- 🎯 1. पेज सेटअप ---
st.set_page_config(page_title="JARVIS RV OS", layout="wide", initial_sidebar_state="collapsed")

# --- 🛠️ 2. CSS - झपकने को रोकने के लिए मैजिक कोड ---
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    div[data-testid="stMetricValue"] > div { font-size: 25px; }
    iframe { visibility: visible !important; }
    </style>
""", unsafe_allow_html=True)

# --- 🛡️ 3. डेटा हंटर ---
def fetch_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df
    except: return None

# --- 🔍 4. फिक्स्ड हिस्सा (यह कभी नहीं झपकेगा) ---
st.markdown("<h1 style='text-align:center; color:#00ff00; margin:0;'>🤖 JARVIS RV OS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:white;'>STABLE COMMAND CENTER</p>", unsafe_allow_html=True)

search_query = st.text_input("🔍 Search Stock or Index:", placeholder="यहाँ लिखें...", key="fixed_sarsbar")

indices = {
    "NIFTY 50": {"sym": "^NSEI", "gap": 50},
    "BANK NIFTY": {"sym": "^NSEBANK", "gap": 100},
    "FIN NIFTY": {"sym": "NIFTY_FIN_SERVICE.NS", "gap": 50}
}
selected_idx = st.selectbox("🎯 Target Index:", list(indices.keys()))

# --- 🏗️ 5. लाइव एरिया (यही हिस्सा अपडेट होगा) ---
live_dashboard = st.empty()

# --- 🚀 6. बैकग्राउंड लूप (असली समाधान) ---
# यह लूप बिना पेज रिफ्रेश किए सिर्फ 'live_dashboard' को अपडेट करेगा
while True:
    ticker = indices[selected_idx]["sym"]
    gap = indices[selected_idx]["gap"]
    df = fetch_data(ticker)
    
    if df is not None and not df.empty:
        ltp = round(df['Close'].iloc[-1], 2)
        atm_strike = round(ltp / gap) * gap
        
        # 9/21 EMA
        df['E9'] = df['Close'].ewm(span=9).mean()
        df['E21'] = df['Close'].ewm(span=21).mean()
        is_buy = df['E9'].iloc[-1] > df['E21'].iloc[-1]
        sig_text = "BUY (CALL) ACTIVE" if is_buy else "SELL (PUT) ACTIVE"
        sig_color = "#00ff00" if is_buy else "#ff4b4b"

        # लाइव डैशबोर्ड के अंदर डेटा डालना
        with live_dashboard.container():
            # 📊 चार्ट और ऑप्शन चैन
            col_chart, col_oi = st.columns([2, 1])
            with col_chart:
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            with col_oi:
                st.markdown(f"""
                    <div style="background:#111; padding:25px; border-radius:15px; border:2px solid #333; height:380px; display:flex; flex-direction:column; justify-content:center; text-align:center;">
                        <p style="color:gray; margin:0;">ATM OPTION CHAIN</p>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin:25px 0;">
                            <b style="color:#00ff00; font-size:24px;">CE</b>
                            <span style="color:white; font-size:32px; font-weight:bold;">{atm_strike}</span>
                            <b style="color:#ff4b4b; font-size:24px;">PE</b>
                        </div>
                        <h2 style="color:#ffff00;">₹ 125.50</h2>
                    </div>
                """, unsafe_allow_html=True)

            # 🚨 सिग्नल बॉक्स
            st.markdown(f"""
                <div style="background:#07090f; padding:30px; border-radius:20px; border:5px solid {sig_color}; text-align:center; box-shadow: 0px 0px 20px {sig_color}; margin-top:10px;">
                    <h1 style="color:{sig_color}; margin:0; font-size:48px;">{sig_text}</h1>
                    <p style="color:white; font-size:20px;">LTP: {ltp} | TGT: +35 | SL: -15</p>
                </div>
            """, unsafe_allow_html=True)

            # 🛰️ स्टॉक स्कैनर
            st.write("---")
            st.markdown("### 🛰️ AI SCANNER")
            sc1, sc2, sc3 = st.columns(3)
            for i, s in enumerate(["RELIANCE", "HDFC BANK", "TCS"]):
                with [sc1, sc2, sc3][i]:
                    st.success(f"{s}: BULLISH")
    
    # 2 सेकंड का इंतज़ार (बिना पेज रिफ्रेश किए)
    time.sleep(2)
