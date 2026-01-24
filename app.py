import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Jarvis Live AI", layout="wide")

# --- ऑटो रिफ्रेश (हर 30 सेकंड में) ---
# यह कोड जार्विस की स्क्रीन को बिना बटन दबाए अपडेट करेगा
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=30000, key="jarvis_refresh")

st.title("🤖 JARVIS : Live Crypto Tracking")

# मार्केट और कॉइन सिलेक्शन
coin = st.sidebar.text_input("कॉइन का नाम (Live Test):", "BTC-USD")

# डेटा फेचिंग (1 Minute Interval के साथ)
def fetch_live_data(ticker):
    try:
        # 1 मिनट का डेटा ताकि आपको हर छोटी हलचल दिखे
        df = yf.download(ticker, period="1d", interval="1m")
        if df.empty: return None
        
        # Multi-index सफाई
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # आपकी 9/21 EMA स्ट्रेटजी
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        return df.tail(60) # सिर्फ आखिरी 60 मिनट का डेटा दिखाएं ताकि मूवमेंट दिखे
    except:
        return None

data = fetch_live_data(coin)

if data is not None:
    # प्राइस और सिग्नल
    last_p = float(data['Close'].iloc[-1])
    st.metric(f"🔴 LIVE PRICE ({coin})", f"${last_p:,.2f}")
    
    # ज़ूम वाला चार्ट (Movement देखने के लिए)
    st.line_chart(data[['Close', 'EMA9', 'EMA21']])
    
    # जार्विस का लाइव फैसला
    if data['EMA9'].iloc[-1] > data['EMA21'].iloc[-1]:
        st.success("🎯 जार्विस सिग्नल: BULLISH (Price is Moving Up!)")
    else:
        st.error("📉 जार्विस सिग्नल: BEARISH (Price is Slipping!)")
else:
    st.warning("डेटा अपडेट हो रहा है... कृपया 5 सेकंड रुकें।")
