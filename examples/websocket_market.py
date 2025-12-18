"""WebSocket Market Data Example

This example demonstrates real-time market data streaming via WebSocket:
- Subscribe to price updates
- Subscribe to order book updates
- Subscribe to your orders, positions, and balance (if authenticated)

All credentials are loaded from .env file automatically.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from standx_sdk import StandXWebSocket

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def on_message(data, stream_type):
    """Handle incoming WebSocket messages"""
    print(f"\n[{stream_type.upper()}] {data}")

def on_error(error):
    """Handle WebSocket errors"""
    print(f"Error: {error}")

def on_close(stream_type, code, msg):
    """Handle WebSocket close"""
    print(f"Connection closed: {stream_type} - {code} - {msg}")

# Initialize WebSocket client with credentials from environment
# Get JWT token - prefer from StandXWalletClient if private key available
jwt_token = os.getenv("STANDX_JWT_TOKEN")
if not jwt_token:
    # Try to generate from private key
    private_key = os.getenv("STANDX_PRIVATE_KEY")
    if private_key:
        from standx_sdk import StandXWalletClient
        client = StandXWalletClient(private_key=private_key, chain=os.getenv("STANDX_CHAIN", "bsc"))
        jwt_token = client.jwt_token
        print(f"Generated JWT from private key for wallet: {client.wallet_address}")

ws = StandXWebSocket(
    jwt_token=jwt_token,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

# Connect to market stream
print("Connecting to market stream...")
ws.connect_market_stream()

# Wait for connection
time.sleep(2)

# Subscribe to price updates
print("Subscribing to BTC-USD price...")
ws.subscribe("price", "BTC-USD")

# Subscribe to order book
print("Subscribing to BTC-USD order book...")
ws.subscribe("depth_book", "BTC-USD")

# If authenticated, subscribe to your orders
if ws.jwt_token:
    print("Subscribing to your orders...")
    ws.subscribe("order")
    
    print("Subscribing to your positions...")
    ws.subscribe("position")
    
    print("Subscribing to your balance...")
    ws.subscribe("balance")

# Keep connection alive
print("\nListening for updates (press Ctrl+C to stop)...")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nDisconnecting...")
    ws.disconnect_market()
