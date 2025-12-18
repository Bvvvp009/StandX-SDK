"""Wallet Authentication Example

This example demonstrates using StandX SDK with just your private key:
- JWT token and ed25519 keys are automatically generated
- No API key/secret needed
- Wallet must be onboarded on StandX platform

⚠️ WARNING: This example places REAL orders when run!
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from standx_sdk import StandXWalletClient, OrderSide, OrderType, TimeInForce

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Initialize client with private key (JWT and ed25519 keys auto-generated)
# If STANDX_JWT_TOKEN is in .env, it will be used instead of generating new one
private_key = os.getenv("STANDX_PRIVATE_KEY")
if not private_key:
    raise ValueError("STANDX_PRIVATE_KEY not found in .env file. Please add it.")

client = StandXWalletClient(
    private_key=private_key,  # Your wallet private key (wallet must be onboarded)
    chain=os.getenv("STANDX_CHAIN", "bsc"),  # bsc, ethereum, or solana
    jwt_token=os.getenv("STANDX_JWT_TOKEN")  # Optional: use existing JWT from .env
)

print(f"Wallet address: {client.wallet_address}")
print(f"JWT token: {'From .env' if os.getenv('STANDX_JWT_TOKEN') else 'Auto-generated'}")

# Query public data (no credentials needed)
price = client.query_symbol_price("BTC-USD")
print(f"\nBTC Price: ${price.last_price}")

# Query your positions (uses JWT token)
positions = client.query_positions()
print(f"\nYour positions: {len(positions)}")
if positions:
    for pos in positions:
        print(f"  {pos.symbol}: {pos.qty} @ ${pos.entry_price}")

# Create order (uses JWT + ed25519 body signature - all auto-generated from private key)
print("\nPlacing order...")
current_price = float(price.last_price)
order_price = current_price * 0.95  # 5% below current price

result = client.create_order(
    symbol="BTC-USD",
    side=OrderSide.BUY,
    order_type=OrderType.LIMIT,
    qty="0.001",
    price=f"{order_price:.2f}",
    time_in_force=TimeInForce.GTC
)

print(f"\n[SUCCESS] Order created!")
print(f"  Request ID: {result.request_id}")
if result.order_id:
    print(f"  Order ID: {result.order_id}")




