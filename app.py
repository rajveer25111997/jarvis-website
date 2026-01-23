import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Jarvis: Multi-Market AI", layout="wide")
st.title("🤖 JARVIS : Crypto & Stock Intelligence")

# साइडबार में मार्केट मोड
market_type = st.sidebar.selectbox("मार्केट चुनें:", ["Stock Market (India)", "Crypto Currency"])

# --- CRYPTO MODE (अभी टेस्ट करने के लिए) ---
if market_type == "Crypto Currency":
    st.subheader("₿ लाइव क्रिप्टो एनालिसिस (24/7 Live)")
    crypto_coin = st.text_input("कॉइन का नाम (जैसे: BTC-USD, ETH-USD, DOGE-USD)", "BTC-USD")
    
    if crypto_coin:
        # क्रिप्टो डेटा (1 घंटे के इंटरवल पर)
        data = yf.download(crypto_coin, period="7d", interval="1h")
        
        if not data.empty:
            # आपकी 9/21 EMA स्ट्रैटेजी
            data['EMA9'] = data['Close'].ewm(span=9, adjust=False).mean()
            data['EMA21'] = data['Close'].ewm(span=21, adjust=False).mean()
            
            # लाइव चार्ट
            st.line_chart(data[['Close', 'EMA9', 'EMA21']])
            
            # जार्विस का फैसला
            last_p = float(data['Close'].iloc[-1])
            last_e9 = float(data['EMA9'].iloc[-1])
            last_e21 = float(data['EMA21'].iloc[-1])
            
            st.divider()
            if last_e9 > last_e21:
                st.success(f"🚀 जार्विस सिग्नल: {crypto_coin} अभी बुलिश है! (9 EMA > 21 EMA)")
            else:
                st.error(f"📉 जार्विस सिग्नल: {crypto_coin} अभी बेयरिश है। सावधानी रखें।")
            
            st.metric("Current Price", f"${last_p:,.2f}")
        else:
            st.error("कॉइन का नाम सही लिखें (जैसे BTC-USD)")

# --- STOCK MODE (जैसा पहले था) ---
else:
    st.info("सर, इंडियन मार्केट अभी बंद है। मंडे सुबह 9:15 पर यह लाइव हो जाएगा। तब तक आप क्रिप्टो मोड टेस्ट करें।")
    # (यहाँ आपका पुराना स्टॉक वाला कोड रहेगा)
