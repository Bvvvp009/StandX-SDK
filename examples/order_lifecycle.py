"""Order Lifecycle Example

This example demonstrates the complete order lifecycle using generated credentials.
It shows:
- Querying current price
- Creating a limit order
- Querying order status
- Querying open orders
- Canceling an order
- Querying order history

Run examples/generate_and_log_credentials.py first to generate credentials.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from standx_sdk import StandXWalletClient, OrderSide, OrderType, TimeInForce

print("=" * 80)
print("Order Lifecycle Example")
print("=" * 80)
print()

# Initialize client
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

symbol = "BTC-USD"

# 1. Query Current Price
print("=" * 80)
print("1. Querying Current Price")
print("=" * 80)
print()

try:
    price_data = client.query_symbol_price(symbol)
    current_price = float(price_data.last_price)
    print(f"Current {symbol} Price: ${current_price}")
    print()
    
    # Calculate order price (5% below current price for buy order)
    order_price = current_price * 0.95
    print(f"Order Price (5% below market): ${order_price:.2f}")
    print()
except Exception as e:
    print(f"Error querying price: {e}")
    sys.exit(1)

# 2. Query Open Orders Before
print("=" * 80)
print("2. Querying Open Orders (Before)")
print("=" * 80)
print()

try:
    open_orders_before = client.query_open_orders(symbol)
    print(f"Open orders count: {len(open_orders_before)}")
    for order in open_orders_before:
        print(f"  Order ID: {order.id}, Side: {order.side}, Qty: {order.qty}, Price: ${order.price}, Status: {order.status}")
    print()
except Exception as e:
    print(f"Error querying open orders: {e}")
    print()

# 3. Create Limit Order (commented out - uncomment to place real order)
print("=" * 80)
print("3. Create Limit Order Example")
print("=" * 80)
print()

print("NOTE: Order creation is commented out for safety.")
print("Uncomment the code below to place a real order.")
print()

# Uncomment below to place a real order:
"""
try:
    print(f"Creating limit buy order:")
    print(f"  Symbol: {symbol}")
    print(f"  Side: BUY")
    print(f"  Quantity: 0.001")
    print(f"  Price: ${order_price:.2f}")
    print(f"  Time in Force: GTC")
    print()
    
    order_result = client.create_order(
        symbol=symbol,
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        qty="0.001",
        price=f"{order_price:.2f}",
        time_in_force=TimeInForce.GTC
    )
    
    print(f"Order Created!")
    print(f"  Request ID: {order_result.request_id}")
    if order_result.order_id:
        order_id = order_result.order_id
        print(f"  Order ID: {order_id}")
    if order_result.cl_ord_id:
        cl_ord_id = order_result.cl_ord_id
        print(f"  Client Order ID: {cl_ord_id}")
    print()
    
    # Wait a moment for order to be processed
    time.sleep(2)
    
except Exception as e:
    print(f"Error creating order: {e}")
    import traceback
    traceback.print_exc()
    print()
"""

# 4. Query Order Status
print("=" * 80)
print("4. Query Order Status")
print("=" * 80)
print()

# Note: Order status query requires order_id or cl_ord_id from order creation
# Uncomment the order creation section above to test this
order_id = None  # Would be set from order_result.order_id
cl_ord_id = None  # Would be set from order_result.cl_ord_id

if order_id or cl_ord_id:
    try:
        if order_id:
            order = client.query_order(symbol=symbol, order_id=order_id)
        else:
            order = client.query_order(symbol=symbol, cl_ord_id=cl_ord_id)
        
        print(f"Order Status:")
        print(f"  Order ID: {order.id}")
        print(f"  Symbol: {order.symbol}")
        print(f"  Side: {order.side}")
        print(f"  Type: {order.order_type}")
        print(f"  Quantity: {order.qty}")
        print(f"  Price: ${order.price}")
        print(f"  Status: {order.status}")
        print(f"  Filled Quantity: {order.fill_qty}")
        print()
    except Exception as e:
        print(f"Error querying order: {e}")
        print()
else:
    print("No order ID available (order creation was not executed)")
    print()

# 5. Query Open Orders After
print("=" * 80)
print("5. Querying Open Orders (After)")
print("=" * 80)
print()

try:
    open_orders_after = client.query_open_orders(symbol)
    print(f"Open orders count: {len(open_orders_after)}")
    if open_orders_after:
        for order in open_orders_after:
            print(f"  Order ID: {order.id}, Side: {order.side}, Qty: {order.qty}, Price: ${order.price}, Status: {order.status}")
    else:
        print("  No open orders")
    print()
except Exception as e:
    print(f"Error querying open orders: {e}")
    print()

# 6. Cancel Order Example (commented out)
print("=" * 80)
print("6. Cancel Order Example")
print("=" * 80)
print()

print("NOTE: Order cancellation is commented out for safety.")
print("Uncomment the code below to cancel an order.")
print()

# Uncomment below to cancel an order:
"""
if open_orders_after:
    order_to_cancel = open_orders_after[0]
    try:
        print(f"Canceling order ID: {order_to_cancel.id}")
        cancel_result = client.cancel_order(order_id=order_to_cancel.id)
        print(f"Cancel Result: {cancel_result.message}")
        print(f"Request ID: {cancel_result.request_id}")
        print()
        
        # Wait a moment
        time.sleep(2)
        
        # Verify cancellation
        try:
            canceled_order = client.query_order(symbol=symbol, order_id=order_to_cancel.id)
            print(f"Order Status After Cancellation: {canceled_order.status}")
        except Exception as e:
            print(f"Order may have been canceled: {e}")
    except Exception as e:
        print(f"Error canceling order: {e}")
        print()
else:
    print("No open orders to cancel")
    print()
"""

# 7. Query Order History
print("=" * 80)
print("7. Query Order History")
print("=" * 80)
print()

try:
    orders = client.query_orders(symbol=symbol, limit=10)
    print(f"Recent orders (last 10): {len(orders)}")
    if orders:
        for i, order in enumerate(orders[:5], 1):  # Show first 5
            print(f"  {i}. Order ID: {order.id}, Side: {order.side}, "
                  f"Qty: {order.qty}, Price: ${order.price}, Status: {order.status}")
    else:
        print("  No orders found")
    print()
except Exception as e:
    print(f"Error querying order history: {e}")
    print()

# 8. Query Trade History
print("=" * 80)
print("8. Query Trade History")
print("=" * 80)
print()

try:
    trades = client.query_trades(symbol=symbol, limit=10)
    print(f"Recent trades (last 10): {len(trades)}")
    if trades:
        for i, trade in enumerate(trades[:5], 1):  # Show first 5
            print(f"  {i}. Trade ID: {trade.id}, Side: {trade.side}, "
                  f"Qty: {trade.qty}, Price: ${trade.price}")
    else:
        print("  No trades found")
    print()
except Exception as e:
    print(f"Error querying trades: {e}")
    print()

print("=" * 80)
print("Order Lifecycle Example Complete!")
print("=" * 80)
print()
print("Note: Order creation and cancellation are commented out for safety.")
print("Uncomment the relevant sections in the code to execute real orders.")

