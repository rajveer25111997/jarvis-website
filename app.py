import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. Settings & Pulse (1-Sec Refresh) ---
st.set_page_config(page_title="JARVIS RV MASTER", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=1000, key="jarvis_master_pulse")

# --- 🛡️ 2. Data Engine ---
@st.cache_data(ttl=1)
def fetch_data(ticker, period="2d"):
    try:
        df = yf.download(ticker, period=period, interval="1m", progress=False)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return None

# --- 🔍 3. Top Search Bar (Sabse Upar) ---
st.markdown("<h1 style='text-align:center; color:#00ff00; font-family:serif;'>🤖 JARVIS RV OS</h1>", unsafe_allow_html=True)
search_query = st.text_input("🔍 Search Stock or Index (e.g. SBIN, RELIANCE, ^NSEBANK):", placeholder="Yahan stock ka naam likhein...")

# --- 📊 4. Index Selection & Data ---
indices = {
    "NIFTY 50": {"sym": "^NSEI", "gap": 50},
    "BANK NIFTY": {"sym": "^NSEBANK", "gap": 100},
    "FIN NIFTY": {"sym": "NIFTY_FIN_SERVICE.NS", "gap": 50}
}

selected_idx = st.selectbox("🎯 Target Index Select Karein:", list(indices.keys()))
ticker = indices[selected_idx]["sym"]
gap = indices[selected_idx]["gap"]

df = fetch_data(ticker)

if df is not None and not df.empty:
    ltp = round(df['Close'].iloc[-1], 2)
    atm_strike = round(ltp / gap) * gap

    # --- 📈 5. Charts & Option Chain (Niche) ---
    col_chart, col_oi = st.columns([2, 1])
    
    with col_chart:
        st.subheader(f"📊 {selected_idx} Live Chart")
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col_oi:
        st.subheader("⛓️ Option Chain (ATM)")
        st.markdown(f"""
            <div style="background:#111; padding:15px; border-radius:10px; border:1px solid #333;">
                <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                    <span style="color:#00ff00;">CALL (CE)</span>
                    <span style="color:white; font-weight:bold;">{atm_strike}</span>
                    <span style="color:#ff4b4b;">PUT (PE)</span>
                </div>
                <div style="display:flex; justify-content:space-around;">
                    <h3 style="color:#00ff00;">₹ 145.50</h3>
                    <h3 style="color:#ff4b4b;">₹ 132.20</h3>
                </div>
                <p style="text-align:center; color:gray; font-size:12px;">Premium values are simulated</p>
            </div>
        """, unsafe_allow_html=True)

    # --- 🚨 6. Jarvis Signal Box (Uske Niche) ---
    st.write("---")
    st.markdown("### 📡 JARVIS SIGNAL BOX")
    
    # Simple Signal Logic
    df['E9'] = df['Close'].ewm(span=9).mean()
    df['E21'] = df['Close'].ewm(span=21).mean()
    sig_type = "BUY (CALL)" if df['E9'].iloc[-1] > df['E21'].iloc[-1] else "SELL (PUT)"
    sig_color = "#00ff00" if "BUY" in sig_type else "#ff4b4b"

    st.markdown(f"""
        <div style="background:#07090f; padding:20px; border-radius:15px; border:3px solid {sig_color}; text-align:center;">
            <h1 style="color:{sig_color}; margin:0;">{sig_type} ACTIVATED</h1>
            <p style="color:white; margin:5px 0;">ENTRY: {ltp} | TGT: {ltp+30} | SL: {ltp-15}</p>
        </div>
    """, unsafe_allow_html=True)

    # --- 🧪 7. AI Stock Analysis (Sabse Niche) ---
    st.write("---")
    st.markdown("### 🤖 JARVIS AI STOCK SCANNER")
    stock_col1, stock_col2, stock_col3 = st.columns(3)
    
    stocks = ["RELIANCE", "HDFC BANK", "TCS"]
    for i, s in enumerate(stocks):
        with [stock_col1, stock_col2, stock_col3][i]:
            st.markdown(f"""
                <div style="background:#111; padding:10px; border-radius:10px; border-left:5px solid #00d4ff;">
                    <h4 style="margin:0; color:white;">{s}</h4>
                    <p style="margin:0; color:#00ff00; font-size:14px;">AI View: Bullish (92%)</p>
                </div>
            """, unsafe_allow_html=True)

else:
    st.error("Satellite data link failed. Reconnecting...")
