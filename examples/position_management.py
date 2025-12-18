"""Position Management Example

This example demonstrates how to manage positions using generated credentials.
It shows:
- Querying positions
- Querying position configuration
- Changing leverage
- Changing margin mode
- Transferring margin

Run examples/generate_and_log_credentials.py first to generate credentials.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from standx_sdk import StandXWalletClient
from standx_sdk.types import MarginMode

print("=" * 80)
print("Position Management Example")
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

# 1. Query All Positions
print("=" * 80)
print("1. Querying All Positions")
print("=" * 80)
print()

try:
    positions = client.query_positions()
    if positions:
        print(f"Found {len(positions)} position(s):")
        print()
        for i, pos in enumerate(positions, 1):
            print(f"Position {i}:")
            print(f"  Symbol: {pos.symbol}")
            print(f"  Quantity: {pos.qty}")
            print(f"  Entry Price: ${pos.entry_price}")
            print(f"  Entry Value: ${pos.entry_value}")
            print(f"  Realized PnL: ${pos.realized_pnl}")
            print(f"  Leverage: {pos.leverage}x")
            print(f"  Margin Mode: {pos.margin_mode}")
            print(f"  Initial Margin: ${pos.initial_margin}")
            print(f"  Status: {pos.status}")
            print()
    else:
        print("No open positions found.")
        print()
except Exception as e:
    print(f"Error querying positions: {e}")
    print()

# 2. Query Position Configuration for a Symbol
symbol = "BTC-USD"
print("=" * 80)
print(f"2. Position Configuration for {symbol}")
print("=" * 80)
print()

try:
    config = client.query_position_config(symbol)
    print(f"Symbol: {config.symbol}")
    print(f"Min Leverage: {config.min_leverage}x")
    print(f"Max Leverage: {config.max_leverage}x")
    print(f"Current Leverage: {config.leverage}x")
    print(f"Current Margin Mode: {config.margin_mode}")
    print()
except Exception as e:
    print(f"Error querying position config: {e}")
    print()

# 3. Example: Change Leverage (commented out - uncomment to execute)
print("=" * 80)
print("3. Change Leverage Example (commented out)")
print("=" * 80)
print()
print("# To change leverage for a position:")
print("# result = client.change_leverage(symbol='BTC-USD', leverage=10)")
print("# print(f'Leverage change result: {result.message}')")
print()

# 4. Example: Change Margin Mode (commented out - uncomment to execute)
print("=" * 80)
print("4. Change Margin Mode Example (commented out)")
print("=" * 80)
print()
print("# To change margin mode:")
print("# result = client.change_margin_mode(")
print("#     symbol='BTC-USD',")
print("#     margin_mode=MarginMode.CROSS  # or MarginMode.ISOLATED")
print("# )")
print("# print(f'Margin mode change result: {result.message}')")
print()

# 5. Example: Transfer Margin (commented out - uncomment to execute)
print("=" * 80)
print("5. Transfer Margin Example (commented out)")
print("=" * 80)
print()
print("# To add margin to a position:")
print("# result = client.transfer_margin(")
print("#     symbol='BTC-USD',")
print("#     amount_in='100.0',")
print("#     direction='add'  # or 'remove'")
print("# )")
print("# print(f'Margin transfer result: {result.message}')")
print()

# 6. Query Position for Specific Symbol
print("=" * 80)
print(f"6. Position Details for {symbol}")
print("=" * 80)
print()

try:
    symbol_positions = client.query_positions(symbol=symbol)
    if symbol_positions:
        pos = symbol_positions[0]
        print(f"Position Details:")
        print(f"  Symbol: {pos.symbol}")
        print(f"  Quantity: {pos.qty}")
        print(f"  Entry Price: ${pos.entry_price}")
        print(f"  Entry Value: ${pos.entry_value}")
        print(f"  Realized PnL: ${pos.realized_pnl}")
        print(f"  Leverage: {pos.leverage}x")
        print(f"  Margin Mode: {pos.margin_mode}")
        print(f"  Initial Margin: ${pos.initial_margin}")
        print(f"  Status: {pos.status}")
    else:
        print(f"No position found for {symbol}")
except Exception as e:
    print(f"Error querying position: {e}")
    print()

print("=" * 80)
print("Position Management Example Complete!")
print("=" * 80)
print()
print("Note: Position modification operations (change leverage, margin mode, transfer)")
print("are commented out for safety. Uncomment them in the code to execute.")

