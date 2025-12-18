"""Order Creation Using .env Credentials

This example demonstrates placing a real order using credentials from .env:
1. Loads private key from .env file
2. Auto-generates JWT token and ed25519 keys
3. Places a real limit order (no placeholders, no mocks)

⚠️ WARNING: This example places REAL orders when run!
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from standx_sdk import StandXWalletClient, OrderSide, OrderType, TimeInForce

print("=" * 70)
print("Order Creation Using Credentials from .env")
print("=" * 70)

# Verify required credentials are in .env
private_key = os.getenv("STANDX_PRIVATE_KEY")
if not private_key:
    print("\n[ERROR] STANDX_PRIVATE_KEY not found in .env file")
    print("\nPlease add your private key to .env:")
    print("STANDX_PRIVATE_KEY=0x_your_private_key_here")
    sys.exit(1)

chain = os.getenv("STANDX_CHAIN", "bsc")
print(f"\nUsing credentials from .env:")
print(f"  Chain: {chain}")
print(f"  Private Key: {'*' * 20}...{private_key[-8:]}")

# Initialize client - JWT will be auto-generated from private key
client = StandXWalletClient(
    private_key=private_key,
    chain=chain
)

print(f"\n[OK] Client initialized")
print(f"  Wallet: {client.wallet_address}")
print(f"  JWT Token: Generated from private key")

# Get current market price
print("\n" + "=" * 70)
print("Step 1: Get Current Market Price")
print("=" * 70)

price_data = client.query_symbol_price("BTC-USD")
current_price = float(price_data.last_price)
print(f"Current BTC Price: ${current_price:,.2f}")
print(f"Mark Price: ${float(price_data.mark_price):,.2f}")

# Check positions
print("\n" + "=" * 70)
print("Step 2: Check Current Positions")
print("=" * 70)

positions = client.query_positions()
print(f"Open positions: {len(positions)}")
if positions:
    for pos in positions:
        print(f"  {pos.symbol}: {pos.qty} @ ${pos.entry_price}")

# Check open orders
print("\n" + "=" * 70)
print("Step 3: Check Open Orders")
print("=" * 70)

open_orders = client.query_open_orders()
print(f"Open orders: {len(open_orders)}")
if open_orders:
    for order in open_orders:
        print(f"  Order {order.id}: {order.side} {order.qty} @ ${order.price}")

# Place order
print("\n" + "=" * 70)
print("Step 4: Place Real Order")
print("=" * 70)

# Calculate order price (5% below current price for buy order)
order_price = current_price * 0.95
order_qty = "0.001"  # Small quantity for testing

print(f"Placing BUY limit order:")
print(f"  Symbol: BTC-USD")
print(f"  Side: BUY")
print(f"  Type: LIMIT")
print(f"  Quantity: {order_qty} BTC")
print(f"  Price: ${order_price:,.2f} (5% below current)")
print(f"  Time In Force: GTC")

try:
    result = client.create_order(
        symbol="BTC-USD",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        qty=order_qty,
        price=f"{order_price:.2f}",
        time_in_force=TimeInForce.GTC
    )
    
    print(f"\n[SUCCESS] Order placed successfully!")
    print(f"  Request ID: {result.request_id}")
    if result.order_id:
        print(f"  Order ID: {result.order_id}")
    if result.cl_ord_id:
        print(f"  Client Order ID: {result.cl_ord_id}")
    
    # Verify order
    print("\n" + "=" * 70)
    print("Step 5: Verify Order")
    print("=" * 70)
    
    if result.order_id:
        try:
            order_details = client.query_order(order_id=result.order_id, symbol="BTC-USD")
            print(f"Order verified:")
            print(f"  ID: {order_details.id}")
            print(f"  Symbol: {order_details.symbol}")
            print(f"  Side: {order_details.side}")
            print(f"  Quantity: {order_details.qty}")
            print(f"  Price: ${order_details.price}")
            print(f"  Status: {order_details.status}")
        except Exception as e:
            print(f"Could not verify order: {e}")
    
except Exception as e:
    print(f"\n[ERROR] Failed to place order: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("[SUCCESS] Order Creation Complete!")
print("=" * 70)
print("\nAll credentials were loaded from .env file:")
print(f"  [OK] Private Key: From STANDX_PRIVATE_KEY")
print(f"  [OK] Chain: {chain}")
print(f"  [OK] JWT Token: Auto-generated from private key")
print(f"  [OK] ed25519 Keys: Auto-generated for body signature")
print("\nNo placeholders or mocks were used - this was a real order!")

