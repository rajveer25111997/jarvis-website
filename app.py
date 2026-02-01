import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. BUDGET DAY CONFIG ---
st.set_page_config(page_title="JARVIS-R: BUDGET SNIPER", layout="wide")
# बजट डे पर 2 सेकंड में रिफ्रेश ज़रूरी है
st_autorefresh(interval=2000, key="budget_live_refresh")

# --- 🧠 2. LIVE DATA ENGINE ---
def get_live_nse_data(symbol):
    try:
        # आज बजट है, इसलिए सिर्फ आज का डेटा ('1d')
        df = yf.download(symbol, period="1d", interval="1m", progress=False, auto_adjust=True)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): 
                df.columns = df.columns.get_level_values(0)
            return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# --- 🔊 3. BUDGET VOICE ALERTS ---
def jarvis_speak(text, type="signal"):
    siren = "https://www.soundjay.com/buttons/sounds/beep-07.mp3" if type=="signal" else "https://www.soundjay.com/buttons/sounds/beep-09.mp3"
    js = f"""
    <script>
    var audio = new Audio('{siren}'); audio.play();
    var m = new SpeechSynthesisUtterance('{text}');
    m.lang = 'hi-IN'; window.speechSynthesis.speak(m);
    </script>
    """
    st.components.v1.html(js, height=0)

# --- 🏦 4. BRANDING ---
st.markdown("""
    <div style='text-align:center; background:linear-gradient(90deg, #ff9933, #ffffff, #128807); padding:15px; border-radius:15px; border:2px solid #000080;'>
        <h1 style='color:blue; margin:0;'>🤖 JARVIS-R: BUDGET DAY SNIPER 2026</h1>
        <p style='color:black; margin:0; font-weight:bold;'>HIGH VOLATILITY MODE ACTIVE | NSE LIVE</p>
    </div>
""", unsafe_allow_html=True)

if st.button("📢 ACTIVATE BUDGET VOICE (इसे अभी दबाएं)", use_container_width=True):
    jarvis_speak("Budget day scanning active. Rajveer Sir, market is highly volatile. Be careful!")

if "last_sig" not in st.session_state: st.session_state.last_sig = ""

# --- 🚀 5. EXECUTION ---
asset = st.sidebar.selectbox("Market:", ["^NSEI", "^NSEBANK", "SBIN.NS", "RELIANCE.NS"])
df = get_live_nse_data(asset)

if not df.empty and len(df) > 5:
    ltp = round(df['Close'].iloc[-1], 2)
    df['E9'] = df['Close'].ewm(span=9).mean()
    df['E21'] = df['Close'].ewm(span=21).mean()
    df['E200'] = df['Close'].ewm(span=200).mean()

    buy_sig = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (ltp > df['E200'].iloc[-1])
    sell_sig = (df['E9'].iloc[-1] < df['E21'].iloc[-1]) and (ltp < df['E200'].iloc[-1])

    # Alerts
    if buy_sig and st.session_state.last_sig != "BUY":
        st.session_state.last_sig = "BUY"
        jarvis_speak(f"Rajveer Sir, Call Signal in {asset}. Positive budget move detected!")
    elif sell_sig and st.session_state.last_sig != "SELL":
        st.session_state.last_sig = "SELL"
        jarvis_speak(f"Rajveer Sir, Put Signal in {asset}. Market reacting negative!")

    # UI
    c1, c2 = st.columns([2, 1])
    with c1:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.add_trace(go.Scatter(x=df.index, y=df['E200'], name='200 EMA', line=dict(color='orange')))
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.metric("LIVE PRICE", f"₹{ltp}")
        st.info(f"SIGNAL: {st.session_state.last_sig}")
        st.warning("⚠️ Budget Alert: आज SL छोटा रखें और प्रॉफिट जल्दी बुक करें।")
else:
    st.error("📡 डेटा लोड हो रहा है... अगर अभी भी खाली दिखे, तो कृपया 9:15 AM का इंतज़ार करें जब मार्केट ट्रेडिंग पूरी तरह शुरू होगी।")
