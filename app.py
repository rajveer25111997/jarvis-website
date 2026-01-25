import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# 1. पेज सेटअप - ब्रोकरेज ऐप जैसा क्लीन लुक
st.set_page_config(page_title="Jarvis Live Terminal", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=1000, key="jarvis_fast_tick") # 1 सेकंड की टिक

# CSS: स्क्रीन को डार्क और प्रोफेशनल बनाने के लिए
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    div[data-testid="stMetricValue"] { font-size: 35px; color: #00ff00; }
    </style>
    """, unsafe_allow_html=True)

# --- डेटा लोडर (केवल लाइव डेटा पर फोकस) ---
@st.cache_data(ttl=1)
def get_live_tick(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if df.empty:
            df = yf.download(ticker, period="5d", interval="5m", progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # 9/21 EMA (आपकी स्ट्रेटजी)
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        return df
    except:
        return None

# --- टॉप हेडर ---
st.markdown("<h2 style='text-align: center; color: white;'>🤖 JARVIS : Live Market Feed</h2>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

def draw_terminal(ticker, label, column):
    data = get_live_tick(ticker)
    with column:
        if data is not None:
            last_price = data['Close'].iloc[-1]
            prev_price = data['Close'].iloc[-2]
            color = "#00ff00" if last_price >= prev_price else "#ff4b4b"
            
            # ब्रोकरेज ऐप जैसा प्राइस टिकर
            st.markdown(f"""
                <div style='background: #161b22; padding: 15px; border-radius: 10px; border-left: 5px solid {color};'>
                    <h4 style='margin:0; color: #8b949e;'>{label}</h4>
                    <h1 style='margin:0; color: {color};'>₹{last_price:,.2f}</h1>
                </div>
            """, unsafe_allow_html=True)
            
            # कैंडलस्टिक चार्ट
            fig = go.Figure(data=[go.Candlestick(
                x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
                name='Price', increasing_line_color='#00ff00', decreasing_line_color='#ff4b4b'
            )])
            
            # EMA लाइन्स जोड़ना
            fig.add_trace(go.Scatter(x=data.index, y=data['EMA9'], name="9 EMA", line=dict(color='orange', width=1.5)))
            fig.add_trace(go.Scatter(x=data.index, y=data['EMA21'], name="21 EMA", line=dict(color='blue', width=1.5)))
            
            fig.update_layout(
                template="plotly_dark", height=500,
                margin=dict(l=0,r=0,t=0,b=0),
                xaxis_rangeslider_visible=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# --- दोनों मार्केट चालू करें ---
draw_terminal("^NSEI", "NIFTY 50", col1)
draw_terminal("BTC-USD", "BITCOIN", col2)

# बॉटम बार
st.markdown("---")
st.caption("Jarvis Data Status: Live (1s Polling) | Strategy: 9/21 EMA Cross")
