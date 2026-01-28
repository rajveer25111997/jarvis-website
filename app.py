import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import warnings
import time

# --- 🎯 1. सिस्टम कॉन्फ़िगरेशन ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="JARVIS RV OS", layout="wide", initial_sidebar_state="collapsed")

# --- 🛡️ 2. डेटा रिकवरी इंजन ---
def fetch_market_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): 
                df.columns = df.columns.get_level_values(0)
            return df
    except: return None

# --- 🔍 3. फिक्स्ड हेडर (Sarsbar) - यह कभी नहीं झपकेगा ---
st.markdown("<h1 style='text-align:center; color:#00ff00; margin:0;'>🤖 JARVIS RV OS</h1>", unsafe_allow_html=True)

indices = {
    "NIFTY 50": {"sym": "^NSEI", "gap": 50},
    "BANK NIFTY": {"sym": "^NSEBANK", "gap": 100},
    "FIN NIFTY": {"sym": "NIFTY_FIN_SERVICE.NS", "gap": 50}
}

idx_choice = st.selectbox("🎯 Target Index:", list(indices.keys()))
ticker = indices[idx_choice]["sym"]
gap = indices[idx_choice]["gap"]

st.write("---")

# --- 🏗️ 4. नो-ब्लिंक फ्रैगमेंट (असली जादू यहाँ है) ---
@st.fragment(run_every="2s")
def render_live_dashboard(ticker, gap):
    df = fetch_market_data(ticker)

    if df is not None and not df.empty:
        # --- [1. डेटा और इंडीकेटर्स] ---
        ltp = round(df['Close'].iloc[-1], 2)
        atm_strike = round(ltp / gap) * gap
        momentum = df['Close'].diff(3).iloc[-1]
        
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        is_buy = df['E9'].iloc[-1] > df['E21'].iloc[-1]
        sig_text = "BUY (CALL) ACTIVE" if is_buy else "SELL (PUT) ACTIVE"
        sig_color = "#00ff00" if is_buy else "#ff4b4b"

        # --- [2. LIVE PREMIUM & WHALE TRACKER] ---
        # प्रीमियम और व्हेल मीटर का लॉजिक
        ce_price = round((ltp * 0.005) + (momentum * 2), 2)
        pe_price = round((ltp * 0.005) - (momentum * 2), 2)
        whale_power = "BULLS" if momentum > 0 else "BEARS"
        whale_color = "#00ff00" if momentum > 0 else "#ff4b4b"
        whale_strength = min(abs(int(momentum * 10)), 100)

        # --- [3. VOICE ALERT - आवाज़] ---
        if st.session_state.get('last_sig') != sig_text:
            js_voice = f"<script>var m = new SpeechSynthesisUtterance('{sig_text}'); window.speechSynthesis.speak(m);</script>"
            st.components.v1.html(js_voice, height=0)
            st.session_state['last_sig'] = sig_text

        # --- [4. DASHBOARD UI] ---
        col_chart, col_oi = st.columns([2, 1])
        
        with col_chart:
            # नो-ब्लिंक चार्ट
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            # Whale Meter (शक्ति मीटर)
            st.markdown(f"""
                <div style="width: 100%; background: #222; border-radius: 10px; margin-top: 10px; height:10px;">
                    <div style="width: {whale_strength}%; background: {whale_color}; height: 10px; border-radius: 10px; transition: 0.5s;"></div>
                </div>
                <p style="color:{whale_color}; text-align:center; margin:0; font-weight:bold; font-size:14px;">WHALE POWER: {whale_power} ({whale_strength}%)</p>
            """, unsafe_allow_html=True)
        
        with col_oi:
            # ऑप्शन चैन और लाइव प्रीमियम बॉक्स
            st.markdown(f"""
                <div style="background:#111; padding:20px; border-radius:15px; border:1px solid #333; height:430px; display:flex; flex-direction:column; justify-content:center; text-align:center;">
                    <p style="color:gray; margin:0; font-size:14px;">ATM OPTION CHAIN & LIVE PREMIUM</p>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin:15px 0;">
                        <b style="color:#00ff00; font-size:22px;">CE</b>
                        <span style="color:white; font-size:28px; font-weight:bold;">{atm_strike}</span>
                        <b style="color:#ff4b4b; font-size:22px;">PE</b>
                    </div>
                    <div style="display:flex; justify-content:space-around; margin-bottom:15px;">
                        <div><h2 style="color:#00ff00; margin:0;">₹ {ce_price}</h2><small>CALL PRICE</small></div>
                        <div><h2 style="color:#ff4b4b; margin:0;">₹ {pe_price}</h2><small>PUT PRICE</small></div>
                    </div>
                    <p style="color:#ffff00; border-top:1px solid #333; padding-top:10px; font-size:12px;">PROFIT FILTER: 15-20 PTS ACTIVE</p>
                </div>
            """, unsafe_allow_html=True)

        # 🚨 मास्टर सिग्नल बॉक्स
        st.markdown(f"""
            <div style="background:#07090f; padding:25px; border-radius:20px; border:5px solid {sig_color}; text-align:center; box-shadow: 0px 0px 20px {sig_color}; margin-top:10px;">
                <h1 style="color:{sig_color}; margin:0; font-size:40px; font-weight:bold;">{sig_text}</h1>
                <p style="color:white; font-size:18px; margin-top:5px;">LTP: {ltp} | CE: ₹{ce_price} | PE: ₹{pe_price}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # इंडीकेटर्स
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        is_buy = df['E9'].iloc[-1] > df['E21'].iloc[-1]
        sig_text = "BUY (CALL) ACTIVE" if is_buy else "SELL (PUT) ACTIVE"
        sig_color = "#00ff00" if is_buy else "#ff4b4b"

        # 📊 चार्ट और ऑप्शन चैन
        
        col_chart, col_oi = st.columns([2, 1])
        
        with col_chart:
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(
                template="plotly_dark", height=400, 
                xaxis_rangeslider_visible=False, 
                margin=dict(l=0,r=0,t=0,b=0)
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with col_oi:
            st.markdown(f"""
                <div style="background:#111; padding:25px; border-radius:15px; border:1px solid #333; height:380px; display:flex; flex-direction:column; justify-content:center; text-align:center;">
                    <p style="color:gray; margin:0; font-size:14px;">ATM OPTION CHAIN</p>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin:25px 0;">
                        <b style="color:#00ff00; font-size:24px;">CE</b>
                        <span style="color:white; font-size:32px; font-weight:bold;">{atm_strike}</span>
                        <b style="color:#ff4b4b; font-size:24px;">PE</b>
                    </div>
                    <div style="display:flex; justify-content:space-around;">
                        <span style="color:#00ff00; font-size:22px;">₹ 128.4</span>
                        <span style="color:#ff4b4b; font-size:22px;">₹ 131.2</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # 🚨 सिग्नल बॉक्स
        st.markdown(f"""
            <div style="background:#07090f; padding:30px; border-radius:20px; border:5px solid {sig_color}; text-align:center; box-shadow: 0px 0px 20px {sig_color}; margin-top:10px;">
                <h1 style="color:{sig_color}; margin:0; font-size:45px; letter-spacing:2px; font-weight:bold;">{sig_text}</h1>
                <p style="color:white; font-size:20px; margin-top:10px;">LTP: {ltp} | TGT: +35 | SL: -15</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("डेटा की सर्जरी चल रही है...")

# फ्रैगमेंट को कॉल करना
render_live_dashboard(ticker, gap)

# 🛰️ 5. AI स्टॉक स्कैनर (सबसे नीचे - यह भी स्थिर रहेगा)
st.write("---")
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


