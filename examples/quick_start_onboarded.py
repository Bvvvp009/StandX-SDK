"""Quick Start Example: Trading with Onboarded Wallet

This example shows the quickest way to start trading with StandX SDK:
- Only requires your private key (wallet must be onboarded)
- JWT token and ed25519 keys are auto-generated
- Demonstrates basic operations: price query, positions, orders

Perfect for getting started quickly!
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

# Verify private key is set
private_key = os.getenv("STANDX_PRIVATE_KEY")
if not private_key:
    print("[ERROR] STANDX_PRIVATE_KEY not found in .env file")
    print("\nPlease add your private key to .env:")
    print("STANDX_PRIVATE_KEY=0x_your_private_key_here")
    print("\nOr run: python examples/generate_jwt_for_env.py")
    exit(1)

# Initialize client with your onboarded wallet's private key
# JWT token and ed25519 keys will be automatically generated from private key
# No API key/secret needed - everything is generated from private key
client = StandXWalletClient(
    private_key=private_key,  # Your wallet private key (wallet must be onboarded)
    chain=os.getenv("STANDX_CHAIN", "bsc")  # bsc, ethereum, or solana
)

print(f"[OK] Connected with wallet: {client.wallet_address}")
print(f"[OK] JWT token generated automatically from private key")
print(f"[OK] ed25519 keys generated for body signature\n")

# Query current price
print("Querying market data...")
price = client.query_symbol_price("BTC-USD")
print(f"   BTC Price: ${price.last_price}")

# Query your positions
print("\nYour positions:")
positions = client.query_positions()
if positions:
    for pos in positions:
        print(f"   {pos.symbol}: {pos.qty} @ ${pos.entry_price}")
else:
    print("   No open positions")

# Query your balances (endpoint may not be available)
print("\nYour balances:")
try:
    balances = client.query_balances()
    if balances:
        for bal in balances:
            print(f"   {bal.asset}: {bal.available} available")
    else:
        print("   No balances found")
except Exception as e:
    print(f"   Balances endpoint not available: {str(e)[:100]}")

# Query open orders
print("\nOpen orders:")
orders = client.query_open_orders()
if orders:
    for order in orders:
        print(f"   Order {order.id}: {order.side} {order.qty} @ ${order.price}")
else:
    print("   No open orders")

# Example: Place a limit order (uncomment to place real order)
# print("\nPlacing order...")
# current_price = float(price.last_price)
# order_price = current_price * 0.95  # 5% below current price
# result = client.create_order(
#     symbol="BTC-USD",
#     side=OrderSide.BUY,
#     order_type=OrderType.LIMIT,
#     qty="0.001",
#     price=f"{order_price:.2f}",
#     time_in_force=TimeInForce.GTC
# )
# print(f"   Order created: Request ID {result.request_id}")

print("\n[OK] Done!")

