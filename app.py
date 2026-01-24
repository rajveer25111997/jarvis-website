import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Jarvis AI Pro", layout="wide")
st.title("🤖 JARVIS : Multi-Market Intelligence")

# साइडबार सेटअप
st.sidebar.header("🕹️ Jarvis Controls")
market = st.sidebar.selectbox("मार्केट चुनें:", ["Crypto Currency", "Indian Stock Market"])

# डेटा लाने और साफ करने का फंक्शन
def fetch_clean_data(ticker):
    try:
        df = yf.download(ticker, period="7d", interval="1h")
        if df.empty:
            return None
        
        # MultiIndex हटाना (KeyError का पक्का इलाज)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # आपकी 9/21 EMA स्ट्रैटेजी
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        return df.dropna()
    except:
        return None

# एनालिसिस मोड
if market == "Crypto Currency":
    st.subheader("₿ लाइव क्रिप्टो (24/7 Analysis)")
    coin = st.text_input("कॉइन डालें (जैसे: BTC-USD)", "BTC-USD")
    data = fetch_clean_data(coin)
    
    if data is not None:
        st.line_chart(data[['Close', 'EMA9', 'EMA21']])
        last_p = float(data['Close'].iloc[-1])
        st.metric("Current Price", f"${last_p:,.2f}")
        
        if data['EMA9'].iloc[-1] > data['EMA21'].iloc[-1]:
            st.success("🎯 जार्विस सिग्नल: BULLISH")
        else:
            st.error("📉 जार्विस सिग्नल: BEARISH")
    else:
        st.warning("डेटा लोड नहीं हो पाया। कृपया सही सिंबल डालें।")

else:
    st.info("🇮🇳 भारतीय बाज़ार मंडे सुबह 9:15 पर लाइव होगा। तब तक क्रिप्टो टेस्ट करें।")
