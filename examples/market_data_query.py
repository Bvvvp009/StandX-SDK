"""Market Data Query Example

This example demonstrates how to query various market data using generated credentials.
It shows:
- Symbol information
- Current prices
- Order book depth
- Recent trades
- Funding rates
- Kline/candlestick data

Run examples/generate_and_log_credentials.py first to generate credentials.
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from standx_sdk import StandXWalletClient

print("=" * 80)
print("Market Data Query Example")
print("=" * 80)
print()

# Initialize client (credentials auto-loaded from .env or generated)
private_key = os.getenv("STANDX_PRIVATE_KEY")
if not private_key:
    print("[ERROR] STANDX_PRIVATE_KEY not found in .env file")
    print("Please run: python examples/generate_and_log_credentials.py")
    sys.exit(1)

client = StandXWalletClient(
    private_key=private_key,
    chain=os.getenv("STANDX_CHAIN", "bsc")
)

print(f"Connected with wallet: {client.wallet_address}")
print()

# Example symbols to query
symbols = ["BTC-USD"]  # Add more symbols as needed

for symbol in symbols:
    print("=" * 80)
    print(f"Market Data for {symbol}")
    print("=" * 80)
    print()
    
    # 1. Symbol Information
    print("1. Symbol Information:")
    print("-" * 80)
    try:
        symbol_info = client.query_symbol_info(symbol)
        print(f"   Symbol: {symbol_info.symbol}")
        print(f"   Base: {symbol_info.base}")
        print(f"   Quote: {symbol_info.quote}")
        print(f"   Min Qty: {symbol_info.min_qty}")
        print(f"   Max Qty: {symbol_info.max_qty}")
        print(f"   Tick Size: {symbol_info.tick_size}")
        print(f"   Step Size: {symbol_info.step_size}")
        print(f"   Status: {symbol_info.status}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # 2. Current Price
    print("2. Current Price:")
    print("-" * 80)
    try:
        price = client.query_symbol_price(symbol)
        print(f"   Last Price: ${price.last_price}")
        print(f"   Index Price: ${price.index_price}")
        print(f"   Mark Price: ${price.mark_price}")
        print(f"   Mid Price: ${price.mid_price}")
        print(f"   Base: {price.base}")
        print(f"   Quote: {price.quote}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # 3. Order Book Depth
    print("3. Order Book Depth (Top 5 levels):")
    print("-" * 80)
    try:
        depth = client.query_depth_book(symbol, limit=5)
        print("   Bids (Buy Orders):")
        if depth.bids:
            for i, bid in enumerate(depth.bids[:5], 1):
                print(f"     {i}. Price: ${bid[0]}, Size: {bid[1]}")
        print("   Asks (Sell Orders):")
        if depth.asks:
            for i, ask in enumerate(depth.asks[:5], 1):
                print(f"     {i}. Price: ${ask[0]}, Size: {ask[1]}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # 4. Recent Trades
    print("4. Recent Trades (Last 5):")
    print("-" * 80)
    try:
        trades = client.query_recent_trades(symbol, limit=5)
        for i, trade in enumerate(trades, 1):
            time_str = datetime.fromtimestamp(trade.timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S') if trade.timestamp else 'N/A'
            print(f"   {i}. Price: ${trade.price}, Size: {trade.qty}, Side: {trade.side}, Time: {time_str}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # 5. Funding Rates
    print("5. Funding Rates:")
    print("-" * 80)
    try:
        # Note: Funding rates endpoint may require start_time parameter
        # For now, we'll skip this or handle the error gracefully
        print("   Note: Funding rates query may require additional parameters")
        print("   Skipping for now to avoid API errors")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # 6. Kline/Candlestick Data
    print("6. Kline Data (Last 5 candles, 1 hour):")
    print("-" * 80)
    try:
        from standx_sdk.types import Resolution
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = int((datetime.now() - timedelta(hours=5)).timestamp() * 1000)
        
        klines = client.get_kline_history(
            symbol=symbol,
            resolution=Resolution.HOUR_1,
            from_time=start_time,
            to_time=end_time,
            limit=5
        )
        for i, kline in enumerate(klines, 1):
            print(f"   {i}. Time: {datetime.fromtimestamp(kline.time / 1000)}, "
                  f"Open: ${kline.open}, High: ${kline.high}, "
                  f"Low: ${kline.low}, Close: ${kline.close}, Volume: {kline.volume}")
    except Exception as e:
        print(f"   Error: {e}")
    print()

print("=" * 80)
print("Market Data Query Complete!")
print("=" * 80)

