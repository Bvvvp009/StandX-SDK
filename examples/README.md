# StandX SDK Examples

> **⚠️ Community Build - Unofficial**  
> This SDK and examples are community-maintained and unofficial.  
> Not officially supported by StandX. Use at your own risk.

This directory contains comprehensive examples demonstrating how to use the StandX SDK with generated credentials.

## Prerequisites

1. Set up your `.env` file with your private key:
   ```
   STANDX_PRIVATE_KEY=0x_your_private_key_here
   STANDX_CHAIN=bsc  # or ethereum, solana
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Examples Overview

All examples use your private key from `.env` file. No API keys needed!

### 1. Generate and Log Credentials
**File:** `generate_and_log_credentials.py`

Generates all necessary credentials from a private key and logs them in multiple formats:
- JSON format (for programmatic use)
- Environment variables format (for .env file)
- Python dictionary format (for direct use in code)

**Usage:**
```bash
python examples/generate_and_log_credentials.py
```

**Output:**
- Generates JWT token
- Derives wallet address
- Creates ed25519 key pair
- Saves credentials to `examples/generated_credentials.json` (in examples directory)
- Verifies credentials work with API

### 2. Market Data Query
**File:** `market_data_query.py`

Demonstrates how to query various market data:
- Symbol information
- Current prices (last, index, mark, mid)
- Order book depth
- Recent trades
- Kline/candlestick data

**Usage:**
```bash
python examples/market_data_query.py
```

**Features:**
- Queries symbol information
- Shows top 5 order book levels
- Displays recent trades
- Retrieves historical kline data

**Note:** Currently configured for BTC-USD. Add more symbols to the `symbols` list as needed.

### 3. Position Management
**File:** `position_management.py`

Shows how to manage trading positions:
- Query all positions
- Query position configuration
- Change leverage (commented out for safety)
- Change margin mode (commented out for safety)
- Transfer margin (commented out for safety)

**Usage:**
```bash
python examples/position_management.py
```

**Note:** Position modification operations are commented out for safety. Uncomment them in the code to execute.

### 4. Order Lifecycle
**File:** `order_lifecycle.py`

Demonstrates the complete order lifecycle:
- Query current price
- Create limit order (commented out for safety)
- Query order status
- Query open orders
- Cancel order (commented out for safety)
- Query order history
- Query trade history

**Usage:**
```bash
python examples/order_lifecycle.py
```

**Note:** Order creation and cancellation are commented out for safety. Uncomment the relevant sections to execute real orders.

### 5. Portfolio Overview
**File:** `portfolio_overview.py`

Provides a comprehensive overview of your trading portfolio:
- Account balances
- Open positions with PnL
- Open orders
- Recent trades
- Portfolio summary statistics

**Usage:**
```bash
python examples/portfolio_overview.py
```

**Features:**
- Formatted tables for easy reading
- Summary statistics
- Total PnL calculations

## Running All Examples

To test all examples in sequence:

```bash
# 1. Generate credentials first
python examples/generate_and_log_credentials.py

# 2. Run other examples (they use credentials from .env)
python examples/market_data_query.py
python examples/position_management.py
python examples/order_lifecycle.py
python examples/portfolio_overview.py
```

## Quick Start Guide

### Step 1: Set Up Your Private Key

Create a `.env` file in the project root with your private key:

```env
STANDX_PRIVATE_KEY=0x_your_private_key_here
STANDX_CHAIN=bsc
```

**Important:** Your wallet must be onboarded on StandX platform first!

### Step 2: Generate Credentials (Optional)

Run the credential generator to see all your credentials:

```bash
python examples/generate_and_log_credentials.py
```

This will:
- Generate a JWT token (valid for 7 days)
- Derive your wallet address
- Create ed25519 key pair for body signatures
- Save credentials to `examples/generated_credentials.json` (gitignored)
- Show you the credentials in multiple formats

**Note:** You don't need to run this step - `StandXWalletClient` auto-generates everything from your private key!

### Step 3: Run Examples

All examples automatically use your private key from `.env`:

```bash
python examples/market_data_query.py
python examples/position_management.py
python examples/order_lifecycle.py
python examples/portfolio_overview.py
```

## Credential Flow

1. **Set Private Key:** Add `STANDX_PRIVATE_KEY` to your `.env` file
2. **Auto-Generation:** `StandXWalletClient` automatically generates:
   - JWT token from your private key
   - ed25519 keys for body signatures
3. **Use in Examples:** All examples load credentials from `.env` automatically

## Safety Notes

- ⚠️ **WARNING:** Some examples (`wallet_auth_example.py`, `order_with_env_credentials.py`) place REAL orders when run
- Most order creation examples are commented out by default for safety
- Position modification examples are commented out by default
- Always test with small amounts first
- Review the code before running examples that place orders
- The `generated_credentials.json` file contains sensitive data and is gitignored

## Additional Examples

### Basic Examples
- `basic_trading.py` - Basic trading operations (queries only, no orders)
- `quick_start_onboarded.py` - Quick start guide (perfect for beginners)
- `generate_jwt_for_env.py` - Generate JWT token for .env (optional)

### Advanced Examples
- `order_management.py` - Order management with WebSocket tracking
- `websocket_market.py` - Real-time market data streaming

### Examples That Place Real Orders ⚠️
- `wallet_auth_example.py` - Wallet authentication with order creation
- `order_with_env_credentials.py` - Order creation using .env credentials

**Warning:** The last two examples place REAL orders when run. Review the code first!

## Troubleshooting

### Credentials Not Found
If you see `"STANDX_PRIVATE_KEY not found"`, make sure:
1. Your `.env` file exists in the **project root** (same directory as `standx_sdk/`)
2. It contains `STANDX_PRIVATE_KEY=0x_your_key` (with or without `0x` prefix)
3. You have `python-dotenv` installed: `pip install python-dotenv`

### Wallet Not Onboarded
If you see authentication errors:
- Your wallet must be onboarded on StandX platform first
- Visit the StandX platform to onboard your wallet
- Make sure you're using the correct chain (bsc, ethereum, or solana)

### API Errors
- **401 Authentication Failed:** Your wallet isn't onboarded or JWT expired (auto-regenerated)
- **404 Not Found:** Endpoint may not be available (e.g., balances endpoint)
- **422 Validation Error:** Check your order parameters (quantity, price, etc.)
- **Network Errors:** Check your internet connection

### Import Errors
If you see `ModuleNotFoundError: No module named 'standx_sdk'`:
- Make sure you're running from the project root
- Examples use `sys.path.insert` to find the SDK automatically
- If issues persist, install the package: `pip install -e .`

### Attribute Errors
If you see attribute errors like `'object' has no attribute 'xyz'`:
- The API response structure may have changed
- Check `standx_sdk/models.py` for the correct attribute names
- Report the issue if it persists

### Order Not Showing Up
- Market orders execute immediately - check your positions
- Limit orders appear in open orders until filled
- Use `query_open_orders()` to see pending orders
- Use `query_trades()` to see executed trades



