# generate_signals.py
import json
from datetime import datetime
import yfinance as yf
import pandas as pd
from smart_money_concept import SMC

def analyze_gold():
    # 1. Fetch gold data (GC=F is Gold Futures) [citation:6][citation:9]
    # Using a 1h interval with 60 days of data provides sufficient history for SMC analysis.
    ticker = "GC=F"
    print(f"Fetching data for {ticker}...")
    df = yf.download(ticker, period="60d", interval="1h", progress=False)
    
    if df.empty:
        raise ValueError("No data returned from yfinance.")

    # Ensure required columns exist and are lowercase
    df = df.rename(columns=str.lower)
    df = df[['open', 'high', 'low', 'close', 'volume']].dropna()

    # 2. Run SMC Analysis [citation:4][citation:17]
    smc = SMC(df)
    
    # Detect Market Structure (BOS & CHoCH)
    # This will indicate the current trend bias.
    structure = smc.market_structure(swing_length=5)
    
    # Detect Fair Value Gaps (FVG)
    fvgs = smc.fair_value_gaps()
    
    # Detect Order Blocks (OB)
    obs = smc.order_blocks()
    
    # 3. Extract the latest signal data
    # We look at the last row to determine the current state.
    last_idx = df.index[-1]
    
    # Determine Bias from the most recent structure event.
    # If the last structure event is a BOS up or CHoCH up, bias is bullish.
    bias = "NEUTRAL"
    structure_level = None
    if len(structure) > 0:
        last_struct = structure.iloc[-1]
        if last_struct['BOS'] == 1 or last_struct['CHOCH'] == 1:
            bias = "BULLISH"
            structure_level = last_struct.get('Level')
        elif last_struct['BOS'] == -1 or last_struct['CHOCH'] == -1:
            bias = "BEARISH"
            structure_level = last_struct.get('Level')

    # Find the nearest untested FVG and Order Block for context.
    # This is a simplified lookup for the dashboard.
    latest_fvg = None
    if len(fvgs) > 0:
        # Get the most recent FVG
        latest_fvg = fvgs.iloc[-1].to_dict()

    latest_ob = None
    if len(obs) > 0:
        latest_ob = obs.iloc[-1].to_dict()

    # 4. Prepare the output payload
    output = {
        "symbol": "XAUUSD",
        "ticker": ticker,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "price": float(df['close'].iloc[-1]),
        "bias": bias,
        "structure_level": float(structure_level) if structure_level else None,
        "nearest_fvg": latest_fvg,
        "nearest_ob": latest_ob,
        "data_points": len(df)
    }

    return output

def main():
    try:
        signal_data = analyze_gold()
        with open("signals.json", "w") as f:
            json.dump(signal_data, f, indent=2)
        print("Successfully wrote signals.json")
    except Exception as e:
        print(f"Error generating signals: {e}")
        # Write an error state so the dashboard doesn't break
        with open("signals.json", "w") as f:
            json.dump({"error": str(e), "timestamp": datetime.utcnow().isoformat() + "Z"}, f, indent=2)

if __name__ == "__main__":
    main()
