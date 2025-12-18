"""Basic Trading Example

This example demonstrates basic trading operations:
- Query current price
- Query your positions
- Query open orders
- Create a limit order (commented out for safety)

All credentials are loaded from .env file automatically.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from standx_sdk import StandXClient, StandXWalletClient, OrderSide, OrderType, TimeInForce

# Load environment variables
# Option 1: Use python-dotenv (recommended)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Option 2: Set environment variables manually or use system env
    pass

# Initialize client with credentials from environment
# Prefer StandXWalletClient (auto-generates credentials from private key)
private_key = os.getenv("STANDX_PRIVATE_KEY")
if private_key:
    client = StandXWalletClient(
        private_key=private_key,
        chain=os.getenv("STANDX_CHAIN", "bsc")
    )
    print(f"Using StandXWalletClient with wallet: {client.wallet_address}")
else:
    # Fallback to StandXClient if no private key
    client = StandXClient(
        jwt_token=os.getenv("STANDX_JWT_TOKEN"),
        api_key=os.getenv("STANDX_API_KEY"),
        api_secret=os.getenv("STANDX_API_SECRET"),
        session_id=os.getenv("STANDX_SESSION_ID")  # Optional
    )

# Query current price
price_data = client.query_symbol_price("BTC-USD")
print(f"Current BTC price: {price_data}")

# Query your positions
positions = client.query_positions()
print(f"\nYour positions: {len(positions)}")
for pos in positions:
    print(f"  {pos.symbol}: {pos.qty} @ {pos.entry_price}")

# Query open orders
orders = client.query_open_orders("BTC-USD")
print(f"\nOpen orders: {len(orders)}")
for order in orders:
    print(f"  Order {order.id}: {order.side} {order.qty} @ {order.price}")

# Create a limit order (commented out for safety - uncomment to place real order)
print("\nOrder creation example (commented out for safety):")
print("# Uncomment below to place a real order:")
print("# result = client.create_order(")
print("#     symbol='BTC-USD',")
print("#     side=OrderSide.BUY,")
print("#     order_type=OrderType.LIMIT,")
print("#     qty='0.01',")
print("#     price='40000',")
print("#     time_in_force=TimeInForce.GTC")
print("# )")
print("# print(f'Order created: {result}')")
print("# if result.order_id:")
print("#     order = client.query_order('BTC-USD', order_id=result.order_id)")
print("#     print(f'Order status: {order.status}')")
