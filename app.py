import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# 1. पेज सेटअप (Wide Layout)
st.set_page_config(page_title="Jarvis Dual Terminal", layout="wide")
st_autorefresh(interval=30000, key="jarvis_dual_refresh")

st.title("🤖 JARVIS : Dual Market Monitor (India & Crypto)")

# --- डेटा फेचिंग फंक्शन ---
def get_market_data(ticker, interval="5m"):
    try:
        df = yf.download(ticker, period="1d", interval=interval, progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        return df
    except: return None

def create_candle_chart(df, name):
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'),
                          go.Scatter(x=df.index, y=df['EMA9'], line=dict(color='orange', width=1.5), name='9 EMA'),
                          go.Scatter(x=df.index, y=df['EMA21'], line=dict(color='blue', width=1.5), name='21 EMA')])
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10, r=10, t=30, b=10), xaxis_rangeslider_visible=False)
    return fig

# --- स्क्रीन को दो हिस्सों में बाँटना (Split Screen) ---
col1, col2 = st.columns(2)

# --- LEFT SIDE: INDIAN MARKET ---
with col1:
    st.header("🇮🇳 Indian Market")
    ind_ticker = st.text_input("Stock/Index:", "^NSEI") # Nifty Default
    ind_data = get_market_data(ind_ticker)
    
    if ind_data is not None:
        st.plotly_chart(create_candle_chart(ind_data, ind_ticker), use_container_width=True)
        curr_p = ind_data['Close'].iloc[-1]
        st.metric(f"{ind_ticker} Live", f"₹{curr_p:,.2f}")
    else:
        st.warning("मंडे सुबह 9:15 पर यहाँ लाइव डेटा दिखेगा। अभी मार्केट बंद है।")

# --- RIGHT SIDE: CRYPTO MARKET ---
with col2:
    st.header("₿ Crypto Market")
    cry_ticker = st.text_input("Crypto Coin:", "BTC-USD")
    cry_data = get_market_data(cry_ticker)
    
    if cry_data is not None:
        st.plotly_chart(create_candle_chart(cry_data, cry_ticker), use_container_width=True)
        curr_p_c = cry_data['Close'].iloc[-1]
        st.metric(f"{cry_ticker} Live", f"${curr_p_c:,.2f}")
    else:
        st.error("क्रिप्टो डेटा लोड नहीं हो रहा।")

st.divider()

# --- BOTTOM SECTION: LIVE WATCHLIST BOXES ---
st.subheader("🔥 Top Traded (Live Watchlist)")
w_col1, w_col2, w_col3, w_col4 = st.columns(4)

# यहाँ हम पॉपुलर स्टॉक्स के छोटे डिब्बे दिखा रहे हैं
tickers = ["RELIANCE.NS", "SBIN.NS", "ETH-USD", "DOGE-USD"]
cols = [w_col1, w_col2, w_col3, w_col4]

for i, t in enumerate(tickers):
    with cols[i]:
        t_data = yf.download(t, period="1d", interval="1m", progress=False)
        if not t_data.empty:
            # लाइन 74: डेटा को नंबर (float) में बदलें
            price = float(t_data['Close'].iloc[-1])
            # लाइन 75: अब इसे डिब्बे में छापें
            st.info(f"**{t}**\n\nPrice: {price:,.2f}")
