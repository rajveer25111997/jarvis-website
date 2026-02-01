import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. LIVE CONFIG ---
st.set_page_config(page_title="JARVIS-R: LIVE BUDGET", layout="wide")
st_autorefresh(interval=3000, key="budget_live_v4") # 3 Second Fast Refresh

# --- 🧠 2. ADVANCED DATA ENGINE ---
def get_live_nse_data(symbol):
    try:
        # बजट के कारण '1d' की जगह '5d' का बफर ताकि डेटा सिंक रहे
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1d", interval="1m")
        if not df.empty:
            return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# --- 🔊 3. VOICE ENGINE ---
def jarvis_speak(text):
    js = f"<script>var m=new SpeechSynthesisUtterance('{text}');window.speechSynthesis.speak(m);</script>"
    st.components.v1.html(js, height=0)

# --- 🏦 4. UI BRANDING ---
st.markdown("""
    <div style='text-align:center; background:linear-gradient(90deg, #FF9933, #FFFFFF, #128807); padding:10px; border-radius:15px; border:2px solid blue;'>
        <h2 style='color:blue; margin:0;'>🤖 JARVIS-R: LIVE BUDGET SNIPER</h2>
        <p style='color:black; margin:0;'>राजवीर सर, बजट की हलचल पर नजर रखें!</p>
    </div>
""", unsafe_allow_html=True)

if st.button("📢 ACTIVATE VOICE (अभी दबाएं)"):
    jarvis_speak("Live Budget Data Active. Ready for signals Rajveer Sir.")

if "last_sig" not in st.session_state: st.session_state.last_sig = ""

# --- 🚀 5. EXECUTION ---
asset = st.sidebar.selectbox("Symbol:", ["^NSEI", "^NSEBANK", "SBIN.NS", "RELIANCE.NS"])
df = get_live_nse_data(asset)

if not df.empty:
    ltp = round(df['Close'].iloc[-1], 2)
    df['E9'] = df['Close'].ewm(span=9).mean()
    df['E21'] = df['Close'].ewm(span=21).mean()
    df['E200'] = df['Close'].ewm(span=200).mean()

    # Signals
    buy_sig = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (ltp > df['E200'].iloc[-1])
    sell_sig = (df['E9'].iloc[-1] < df['E21'].iloc[-1]) and (ltp < df['E200'].iloc[-1])

    if buy_sig and st.session_state.last_sig != "BUY":
        st.session_state.last_sig = "BUY"
        jarvis_speak(f"Master Buy Signal in {asset} at {ltp}.")
    elif sell_sig and st.session_state.last_sig != "SELL":
        st.session_state.last_sig = "SELL"
        jarvis_speak(f"Master Sell Signal in {asset} at {ltp}.")

    # --- 📺 DISPLAY ---
    c1, c2 = st.columns([2, 1])
    with c1:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.add_trace(go.Scatter(x=df.index, y=df['E200'], name='200 EMA', line=dict(color='orange')))
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.metric("LTP", f"₹{ltp}", delta=f"{round(ltp - df['Open'].iloc[0], 2)}")
        st.info(f"Signal: {st.session_state.last_sig}")
        st.write("📈 **Strategy: 9/21/200 EMA**")
else:
    st.warning("📡 बाज़ार खुला है पर डेटा सिंक हो रहा है... 1 मिनट रुकें या सिंबल बदलें।")
