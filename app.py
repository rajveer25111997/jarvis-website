import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go

# Website Title & Layout
st.set_page_config(page_title="Raju's Jarvis Backtester", layout="wide")
st.title("📈 Jarvis Smart Money Backtester (v2.0)")

# Sidebar for User Inputs
st.sidebar.header("Strategy Settings")
symbol = st.sidebar.text_input("Enter Ticker (e.g., ^NSEI or RELIANCE.NS)", "^NSEI")
timeframe = st.sidebar.selectbox("Timeframe", ("15m", "1h", "1d"), index=1)
period = st.sidebar.selectbox("History Period", ("1mo", "6mo", "1y", "2y"), index=2)

# 1. Data Loading Function
@st.cache_data
def get_data(ticker, tf, prd):
    try:
        data = yf.download(ticker, period=prd, interval=tf)
        # Multi-index columns fix if any
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

df = get_data(symbol, timeframe, period)

if not df.empty:
    # 2. Indicators Calculation (Optimized)
    df['EMA9'] = ta.ema(df['Close'], length=9)
    df['EMA21'] = ta.ema(df['Close'], length=21)
    df['EMA44'] = ta.ema(df['Close'], length=44)
    df['EMA200'] = ta.ema(df['Close'], length=200)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    # MACD Calculation with Flexible Column Selection
    macd_data = ta.macd(df['Close'])
    if macd_data is not None:
        df['MACD'] = macd_data.iloc[:, 0]    # MACD Line
        df['MACD_S'] = macd_data.iloc[:, 2]  # Signal Line
    
    # SMC - Bullish Fair Value Gap (FVG)
    # Logic: Previous Candle High < Next Candle Low
    df['FVG'] = (df['Low'].shift(-2) > df['High']) & (df['Close'].shift(-1) > df['High'])

    # 3. Backtesting Logic (1:1 Risk Reward)
    trades = []
    in_position = False
    
    for i in range(200, len(df)-5):
        # Entry Rules:
        # - Trend: Price > EMA200
        # - Momentum: EMA9 > EMA21
        # - Strength: RSI > 50
        # - MACD: MACD > Signal
        # - SMC: FVG detected
        condition = (
            df['Close'].iloc[i] > df['EMA200'].iloc[i] and
            df['EMA9'].iloc[i] > df['EMA21'].iloc[i] and
            df['RSI'].iloc[i] > 50 and
            df['MACD'].iloc[i] > df['MACD_S'].iloc[i] and
            df['FVG'].iloc[i-1]
        )

        if condition and not in_position:
            entry_price = float(df['Close'].iloc[i])
            stop_loss = float(df['Low'].iloc[i-1]) 
            risk = entry_price - stop_loss
            
            if risk > 0:
                target = entry_price + risk
                in_position = True
                
                # Check outcome in future candles
                for j in range(i+1, len(df)):
                    if df['Low'].iloc[j] <= stop_loss:
                        trades.append({'Date': df.index[j], 'Type': 'Buy', 'Result': 'Loss', 'Profit': -risk})
                        in_position = False
                        break
                    elif df['High'].iloc[j] >= target:
                        trades.append({'Date': df.index[j], 'Type': 'Buy', 'Result': 'Win', 'Profit': risk})
                        in_position = False
                        break

    # 4. Display Results in Dashboard
    trade_df = pd.DataFrame(trades)
    
    col1, col2, col3, col4 = st.columns(4)
    if not trade_df.empty:
        win_rate = (trade_df['Result'] == 'Win').mean() * 100
        total_pnl = trade_df['Profit'].sum()
        
        col1.metric("Total Trades", len(trade_df))
        col2.metric("Win Rate", f"{win_rate:.2f}%")
        col3.metric("Net Profit", f"{total_pnl:.2f}")
        col4.metric("Avg. Profit/Trade", f"{(total_pnl/len(trade_df)):.2f}")
        
        # Interactive Chart
        st.subheader(f"Price Analysis: {symbol}")
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Candles")])
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], line=dict(color='orange', width=2), name="EMA 200"))
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA9'], line=dict(color='blue', width=1), name="EMA 9"))
        fig.update_layout(height=600, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Recent Trade History")
        st.dataframe(trade_df.sort_values(by='Date', ascending=False))
    else:
        st.warning("Strategy ke hisaab se koi trades nahi mile. Timeframe ya ticker change karke dekhein.")
else:
    st.error("Data load nahi ho pa raha hai. Kya aapka internet ya ticker sahi hai?")
