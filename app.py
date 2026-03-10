import yfinance as yf
import pandas as pd
import pandas_ta as ta

def run_backtest(symbol="^NSEI"):
    print(f"--- Fetching Data for {symbol} ---")
    
    # 1. Data Download (1 Year, 1 Hour candles for better SMC/EMA accuracy)
    df = yf.download(symbol, period="1y", interval="1h", progress=False)
    
    if df.empty:
        print("Data nahi mila! Symbol check karein.")
        return

    # 2. Indicators Calculation
    df['EMA9'] = ta.ema(df['Close'], length=9)
    df['EMA21'] = ta.ema(df['Close'], length=21)
    df['EMA44'] = ta.ema(df['Close'], length=44)
    df['EMA200'] = ta.ema(df['Close'], length=200)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    macd = ta.macd(df['Close'])
    df['MACD'] = macd['MACD_12_26_9']
    df['MACD_S'] = macd['MACDs_12_26_9']

    # 3. SMC - Fair Value Gap (FVG) Detection
    # Bullish FVG: Candle 1 High < Candle 3 Low
    df['FVG_Bullish'] = (df['Low'].shift(-2) > df['High']) & (df['Close'].shift(-1) > df['High'])

    # 4. Backtesting Variables
    trades = []
    in_position = False
    
    print("Backtesting Strategy: EMA Cross + RSI + MACD + SMC (1:1 RR)...")

    for i in range(200, len(df)-5):
        # Entry Conditions (Aapki Strategy):
        # - Price above 200 EMA (Long Term Trend)
        # - EMA 9 > 21 (Short Term Momentum)
        # - RSI > 50
        # - MACD > Signal Line
        # - FVG Bullish detected (Smart Money Entry)
        
        condition = (
            df['Close'].iloc[i] > df['EMA200'].iloc[i] and
            df['EMA9'].iloc[i] > df['EMA21'].iloc[i] and
            df['RSI'].iloc[i] > 50 and
            df['MACD'].iloc[i] > df['MACD_S'].iloc[i] and
            df['FVG_Bullish'].iloc[i-1]
        )

        if condition and not in_position:
            entry_price = float(df['Close'].iloc[i])
            stop_loss = float(df['Low'].iloc[i-1]) # Previous candle low
            risk = entry_price - stop_loss
            
            if risk <= 0: continue # Invalid SL protection
            
            target = entry_price + risk # 1:1 Risk Reward
            in_position = True
            
            # Check for TP or SL in next candles
            for j in range(i+1, len(df)):
                current_low = float(df['Low'].iloc[j])
                current_high = float(df['High'].iloc[j])
                
                if current_low <= stop_loss:
                    trades.append({'Result': 'Loss', 'Profit': -risk})
                    in_position = False
                    break
                elif current_high >= target:
                    trades.append({'Result': 'Win', 'Profit': risk})
                    in_position = False
                    break

    # 5. Result Summary
    if trades:
        results_df = pd.DataFrame(trades)
        win_rate = (results_df['Result'] == 'Win').mean() * 100
        total_profit = results_df['Profit'].sum()
        
        print("\n" + "="*30)
        print(f"REPORT FOR: {symbol}")
        print(f"Total Trades: {len(results_df)}")
        print(f"Wins: {len(results_df[results_df['Result'] == 'Win'])}")
        print(f"Losses: {len(results_df[results_df['Result'] == 'Loss'])}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Net Profit (Points): {total_profit:.2f}")
        print("="*30)
    else:
        print("\nKoi trades nahi mile. Strategy settings ya filters thode loose karein.")

# Run for Nifty 50
run_backtest("^NSEI")
