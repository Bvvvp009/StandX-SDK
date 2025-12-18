"""Order Management Example with WebSocket Tracking

This example demonstrates:
- Order management with WebSocket order response tracking
- Real-time order status updates via WebSocket
- Order creation and cancellation (commented out for safety)

All credentials are loaded from .env file automatically.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import uuid
from standx_sdk import StandXClient, StandXWalletClient, StandXWebSocket, OrderSide, OrderType, TimeInForce

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Use session ID from environment or generate new one
session_id = os.getenv("STANDX_SESSION_ID") or str(uuid.uuid4())

# Initialize HTTP client with credentials from environment
# Prefer StandXWalletClient (auto-generates credentials from private key)
private_key = os.getenv("STANDX_PRIVATE_KEY")
if private_key:
    client = StandXWalletClient(
        private_key=private_key,
        chain=os.getenv("STANDX_CHAIN", "bsc"),
        session_id=session_id
    )
    jwt_token = client.jwt_token
    print(f"Using StandXWalletClient with wallet: {client.wallet_address}")
else:
    # Fallback to StandXClient if no private key
    client = StandXClient(
        jwt_token=os.getenv("STANDX_JWT_TOKEN"),
        api_key=os.getenv("STANDX_API_KEY"),
        api_secret=os.getenv("STANDX_API_SECRET"),
        session_id=session_id
    )
    jwt_token = os.getenv("STANDX_JWT_TOKEN")

# Initialize WebSocket for order responses
order_responses = {}

def on_order_response(data, stream_type):
    """Handle order response from WebSocket"""
    request_id = data.get("request_id")
    if request_id:
        order_responses[request_id] = data
        if data.get("code") == 0:
            print(f"[SUCCESS] Order {request_id} successful")
        else:
            print(f"[ERROR] Order {request_id} rejected: {data.get('message')}")

ws = StandXWebSocket(
    jwt_token=jwt_token,
    session_id=session_id,
    on_message=on_order_response
)

# Connect to order response stream
print("Connecting to order response stream...")
ws.connect_order_stream()
time.sleep(2)

# Create order via HTTP (will get response via WebSocket) - commented out for safety
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
print("# request_id = result.request_id")
print("# print(f'Order submitted, request_id: {request_id}')")
print("# # Wait for WebSocket response...")
print("# # Cancel order if needed...")

# Query order status (real API call)
orders = client.query_open_orders("BTC-USD")
print(f"\nOpen orders: {len(orders)}")
for order in orders:
    print(f"  Order {order.id}: {order.side} {order.qty} @ {order.price}")

ws.disconnect_order()
