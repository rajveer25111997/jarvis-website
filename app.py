import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time

# --- [SYSTEM SETUP] ---
st.set_page_config(page_title="JARVIS REAL-TIME", layout="wide")

def fetch_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df
    except: return None

# --- [HEADER] ---
st.markdown("<h1 style='text-align:center; color:#00ff00;'>🤖 JARVIS REAL-TIME OS</h1>", unsafe_allow_html=True)

indices = {"NIFTY 50": {"sym": "^NSEI", "gap": 50}, "BANK NIFTY": {"sym": "^NSEBANK", "gap": 100}}
idx_choice = st.sidebar.selectbox("🎯 Index:", list(indices.keys()))
ticker = indices[idx_choice]["sym"]
gap = indices[idx_choice]["gap"]

live_area = st.empty()

@st.fragment(run_every="2s")
def render_dashboard(ticker, gap):
    df = fetch_data(ticker)
    if df is not None and not df.empty:
        ltp = round(df['Close'].iloc[-1], 2)
        atm_strike = round(ltp / gap) * gap
        
        # ✅ SMART REAL PRICE FINDER
        # हम आने वाली एक्सपायरी का सिंबल तैयार कर रहे हैं (e.g., NIFTY2612321500CE.NS)
        # नोट: yfinance में ऑप्शन सिंबल कभी-कभी अलग हो सकते हैं
        symbol_prefix = "NIFTY" if "NSEI" in ticker else "BANKNIFTY"
        current_year = time.strftime("%y")
        # यह एक अंदाज़न सिंबल है जो Yahoo Finance सपोर्ट करता है
        opt_ticker = f"{symbol_prefix}{current_year}JAN{atm_strike}CE.NS" 
        
        # असली भाव लाने की कोशिश
        try:
            opt_df = yf.download(opt_ticker, period="1d", interval="1m", progress=False)
            if not opt_df.empty:
                real_opt_price = round(opt_df['Close'].iloc[-1], 2)
                data_source = "NSE REAL-TIME"
            else:
                # BACKUP: अगर सिंबल नहीं मिला तो स्मार्ट कैलकुलेशन
                real_opt_price = round(55 + (abs(ltp - atm_strike) * 0.55), 2)
                data_source = "JARVIS CALCULATED"
        except:
            real_opt_price = round(55 + (abs(ltp - atm_strike) * 0.55), 2)
            data_source = "JARVIS CALCULATED"

        # Strategy logic
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        is_buy = df['E9'].iloc[-1] > df['E21'].iloc[-1]
        sig_text = "BUY (CALL)" if is_buy else "SELL (PUT)"
        sig_color = "#00ff00" if is_buy else "#ff4b4b"

        with live_area.container():
            col1, col2 = st.columns([2, 1])
            with col1:
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True, key=f"c_{time.time()}")
            
            with col2:
                st.markdown(f"""
                    <div style="background:#111; padding:20px; border-radius:15px; border:1px solid #333; text-align:center; height:400px; display:flex; flex-direction:column; justify-content:center;">
                        <p style="color:gray;">DATA SOURCE: {data_source}</p>
                        <h2 style="color:white; margin:0;">ATM: {atm_strike}</h2>
                        <h1 style="color:{sig_color}; font-size:50px;">₹{real_opt_price}</h1>
                        <p style="color:white;">OPTION PRICE</p>
                    </div>
                """, unsafe_allow_html=True)

            # 🚨 SIGNAL BOX
            st.markdown(f"""
                <div style="background:#07090f; padding:25px; border-radius:20px; border:5px solid {sig_color}; text-align:center; box-shadow: 0px 0px 20px {sig_color};">
                    <h1 style="color:{sig_color}; margin:0; font-size:45px;">{sig_text} ACTIVE</h1>
                    <p style="color:white; font-size:20px;">ENTRY: ₹{real_opt_price} | TGT: ₹{round(real_opt_price+18,2)} | SL: ₹{round(real_opt_price-8,2)}</p>
                </div>
            """, unsafe_allow_html=True)

render_dashboard(ticker, gap)
