# StandX Python SDK

> **⚠️ Community Build - Unofficial**  
> This is a community-maintained, unofficial Python SDK for the StandX Perpetual Futures API.  
> It is not officially supported by StandX. Use at your own risk.

A comprehensive Python SDK for interacting with the StandX Perpetual Futures API.

## Features

- ✅ Complete HTTP API coverage (all endpoints)
- ✅ WebSocket support for real-time market data
- ✅ WebSocket order response stream
- ✅ Type-safe enums and data structures
- ✅ Comprehensive error handling
- ✅ Request signing for authenticated endpoints
- ✅ JWT token authentication

## Installation

```bash
pip install -r requirements.txt
```

Or install the package:

```bash
pip install -e .
```

## Quick Start

### Using Wallet Private Key (Recommended for Onboarded Wallets)

If your wallet is already onboarded on StandX, you can generate JWT automatically from your private key:

```python
import os
from standx_sdk import StandXWalletClient, OrderSide, OrderType, TimeInForce
from dotenv import load_dotenv

load_dotenv()

# Initialize with private key (JWT and ed25519 keys auto-generated)
# Wallet must be onboarded on StandX platform first
client = StandXWalletClient(
    private_key=os.getenv("STANDX_PRIVATE_KEY"),  # Your wallet private key
    chain="bsc"  # or "ethereum" or "solana"
)

# Query your positions (uses auto-generated JWT)
positions = client.query_positions()
for pos in positions:
    print(f"{pos.symbol}: {pos.qty} @ {pos.entry_price}")

# Place an order
order = client.create_order(
    symbol="BTC-USD",
    side=OrderSide.BUY,
    order_type=OrderType.LIMIT,
    qty="0.01",
    price="40000",
    time_in_force=TimeInForce.GTC
)
```

**Environment Variables:**
```env
STANDX_PRIVATE_KEY=0x_your_private_key_here
STANDX_CHAIN=bsc  # or ethereum, solana
```

**Note:** `StandXWalletClient` automatically generates JWT token and ed25519 keys from your private key. No API key/secret needed!

### Basic Usage (Manual JWT)

```python
from standx_sdk import StandXClient, OrderSide, OrderType, TimeInForce

# Initialize client with JWT token
client = StandXClient(jwt_token="your_jwt_token")

# Query public market data
price = client.query_symbol_price("BTC-USD")
print(price)

# Query your positions
positions = client.query_positions()
for pos in positions:
    print(f"{pos.symbol}: {pos.qty} @ {pos.entry_price}")
```

### Trading with Signed Requests

```python
from standx_sdk import StandXClient, OrderSide, OrderType, TimeInForce

# Initialize with API credentials for trading
client = StandXClient(
    jwt_token="your_jwt_token",
    api_key="your_api_key",
    api_secret="your_api_secret",
    session_id="your_session_id"  # For WebSocket order tracking
)

# Create a limit order
result = client.create_order(
    symbol="BTC-USD",
    side=OrderSide.BUY,
    order_type=OrderType.LIMIT,
    qty="0.1",
    price="50000",
    time_in_force=TimeInForce.GTC
)
print(result)

# Cancel an order
client.cancel_order(order_id=12345)
```

### WebSocket Market Data

```python
from standx_sdk import StandXWebSocket

def on_message(data, stream_type):
    print(f"Received from {stream_type}: {data}")

def on_error(error):
    print(f"Error: {error}")

# Initialize WebSocket client
ws = StandXWebSocket(
    jwt_token="your_jwt_token",
    on_message=on_message,
    on_error=on_error
)

# Connect to market stream
ws.connect_market_stream()

# Subscribe to price updates
ws.subscribe("price", "BTC-USD")

# Subscribe to order book
ws.subscribe("depth_book", "BTC-USD")

# Subscribe to your orders
ws.subscribe("order")

# Keep connection alive
import time
time.sleep(60)  # Run for 60 seconds
```

### WebSocket Order Response Stream

```python
from standx_sdk import StandXWebSocket

def on_order_response(data, stream_type):
    if data.get("code") == 0:
        print(f"Order successful: {data}")
    else:
        print(f"Order rejected: {data}")

# Initialize with API credentials
ws = StandXWebSocket(
    jwt_token="your_jwt_token",
    api_key="your_api_key",
    api_secret="your_api_secret",
    session_id="your_session_id",  # Must match HTTP client
    on_message=on_order_response
)

# Connect to order response stream
ws.connect_order_stream()

# Create order via WebSocket
request_id = ws.create_order_ws(
    symbol="BTC-USD",
    side="buy",
    order_type="limit",
    qty="0.1",
    price="50000",
    time_in_force="gtc"
)

# Wait for response
import time
time.sleep(5)
```

## API Reference

### StandXClient

Main client for HTTP API interactions.

#### Initialization

```python
client = StandXClient(
    jwt_token: Optional[str] = None,
    api_key: Optional[str] = None,
    api_secret: Optional[str] = None,
    base_url: Optional[str] = None,
    session_id: Optional[str] = None
)
```

#### Trading Methods

- `create_order()` - Create a new order
- `cancel_order()` - Cancel an order
- `cancel_orders()` - Cancel multiple orders
- `change_leverage()` - Change position leverage
- `change_margin_mode()` - Change margin mode
- `transfer_margin()` - Transfer margin to/from position

#### Query Methods

- `query_order()` - Query order details
- `query_orders()` - Query user orders
- `query_open_orders()` - Query open orders
- `query_trades()` - Query user trades
- `query_positions()` - Query positions
- `query_balances()` - Query balances
- `query_position_config()` - Query position configuration

#### Public Methods

- `query_symbol_info()` - Get symbol information
- `query_symbol_market()` - Get market data
- `query_symbol_price()` - Get current price
- `query_depth_book()` - Get order book
- `query_recent_trades()` - Get recent trades
- `query_funding_rates()` - Get funding rates
- `get_kline_history()` - Get candlestick data
- `get_server_time()` - Get server time
- `health()` - Health check

### StandXWebSocket

WebSocket client for real-time data.

#### Market Stream Channels

- `price` - Real-time price updates
- `depth_book` - Order book updates
- `order` - Your order updates (authenticated)
- `position` - Your position updates (authenticated)
- `balance` - Your balance updates (authenticated)
- `trade` - Your trade updates (authenticated)

#### Methods

- `connect_market_stream()` - Connect to market data stream
- `connect_order_stream()` - Connect to order response stream
- `subscribe()` - Subscribe to a channel
- `create_order_ws()` - Create order via WebSocket
- `cancel_order_ws()` - Cancel order via WebSocket
- `authenticate_market()` - Authenticate market stream
- `disconnect_market()` - Disconnect market stream
- `disconnect_order()` - Disconnect order stream

## Types and Enums

```python
from standx_sdk import (
    OrderSide,      # BUY, SELL
    OrderType,      # LIMIT, MARKET
    OrderStatus,    # OPEN, CANCELED, FILLED, REJECTED, UNTRIGGERED
    TimeInForce,    # GTC, IOC, ALO
    MarginMode,     # CROSS, ISOLATED
    Resolution,     # TICK, SEC_3, MIN_1, MIN_5, etc.
)
```

## Error Handling

```python
from standx_sdk import (
    StandXAPIError,
    StandXAuthenticationError,
    StandXRequestError,
    StandXWebSocketError
)

try:
    client.create_order(...)
except StandXAuthenticationError as e:
    print(f"Auth failed: {e}")
except StandXRequestError as e:
    print(f"Request failed: {e}")
except StandXAPIError as e:
    print(f"API error [{e.code}]: {e.message}")
```

## Examples

See the `examples/` directory for comprehensive examples:

**Getting Started:**
- `quick_start_onboarded.py` - Quick start guide (perfect for beginners)
- `generate_and_log_credentials.py` - Generate and view all credentials
- `basic_trading.py` - Basic trading operations (queries only)

**Market Data:**
- `market_data_query.py` - Query symbol info, prices, order book, trades, klines
- `websocket_market.py` - Real-time market data streaming

**Trading:**
- `order_lifecycle.py` - Complete order lifecycle (create, query, cancel)
- `order_management.py` - Order management with WebSocket tracking
- `position_management.py` - Position management and configuration
- `portfolio_overview.py` - Comprehensive portfolio overview

**Advanced:**
- `wallet_auth_example.py` - Wallet authentication (⚠️ places real orders)
- `order_with_env_credentials.py` - Order creation example (⚠️ places real orders)

See `examples/README.md` for detailed documentation and usage instructions.

## Requirements

- Python 3.8+
- requests
- websocket-client

## License

MIT

## Support

For API documentation, visit: https://docs.standx.com/standx-api/standx-api








