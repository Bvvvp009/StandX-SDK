"""Portfolio Overview Example

This example provides a comprehensive overview of your trading portfolio using generated credentials.
It shows:
- Account balances
- Open positions with PnL
- Open orders
- Recent trades
- Portfolio summary statistics

Run examples/generate_and_log_credentials.py first to generate credentials.
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from standx_sdk import StandXWalletClient

print("=" * 80)
print("Portfolio Overview")
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

print(f"Wallet Address: {client.wallet_address}")
print(f"Chain: {client.chain}")
print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 1. Account Balances
print("=" * 80)
print("1. Account Balances")
print("=" * 80)
print()

try:
    balances = client.query_balances()
    if balances:
        total_balance = 0
        print(f"{'Token':<15} {'Free':<20} {'Locked':<20} {'Total':<20}")
        print("-" * 80)
        for bal in balances:
            free = float(bal.free) if bal.free else 0
            locked = float(bal.locked) if bal.locked else 0
            total_val = float(bal.total) if bal.total else (free + locked)
            total_balance += total_val
            print(f"{bal.token or 'N/A':<15} {free:<20.8f} {locked:<20.8f} {total_val:<20.8f}")
        print("-" * 80)
        print(f"{'TOTAL':<15} {'':<20} {'':<20} {total_balance:<20.8f}")
    else:
        print("No balances found")
    print()
except Exception as e:
    print(f"Error querying balances: {e}")
    print()

# 2. Open Positions
print("=" * 80)
print("2. Open Positions")
print("=" * 80)
print()

try:
    positions = client.query_positions()
    if positions:
        total_unrealized_pnl = 0
        print(f"{'Symbol':<15} {'Qty':<15} {'Entry':<15} {'Entry Value':<15} {'PnL':<20} {'Leverage':<10} {'Status':<10}")
        print("-" * 80)
        for pos in positions:
            qty = float(pos.qty) if pos.qty else 0
            entry_price = float(pos.entry_price) if pos.entry_price else 0
            entry_value = float(pos.entry_value) if pos.entry_value else 0
            realized_pnl = float(pos.realized_pnl) if pos.realized_pnl else 0
            total_unrealized_pnl += realized_pnl
            
            pnl_str = f"${realized_pnl:.2f}"
            if realized_pnl > 0:
                pnl_str = f"+{pnl_str}"
            
            print(f"{pos.symbol:<15} {qty:<15.8f} ${entry_price:<14.2f} ${entry_value:<14.2f} {pnl_str:<20} {pos.leverage or 'N/A'}x {pos.status or 'N/A':<10}")
        print("-" * 80)
        total_pnl_str = f"${total_unrealized_pnl:.2f}"
        if total_unrealized_pnl > 0:
            total_pnl_str = f"+{total_pnl_str}"
        print(f"{'TOTAL UNREALIZED PNL':<15} {'':<8} {'':<15} {'':<15} {'':<15} {total_pnl_str:<20}")
        print(f"\nTotal Positions: {len(positions)}")
    else:
        print("No open positions")
    print()
except Exception as e:
    print(f"Error querying positions: {e}")
    print()

# 3. Open Orders
print("=" * 80)
print("3. Open Orders")
print("=" * 80)
print()

try:
    orders = client.query_open_orders()
    if orders:
        print(f"{'Order ID':<15} {'Symbol':<15} {'Side':<8} {'Type':<10} {'Qty':<15} {'Price':<15} {'Status':<15}")
        print("-" * 80)
        for order in orders:
            qty = float(order.qty) if order.qty else 0
            price = float(order.price) if order.price else 0
            print(f"{order.id:<15} {order.symbol:<15} {order.side:<8} {order.order_type:<10} {qty:<15.8f} ${price:<14.2f} {order.status:<15}")
        print(f"\nTotal Open Orders: {len(orders)}")
    else:
        print("No open orders")
    print()
except Exception as e:
    print(f"Error querying open orders: {e}")
    print()

# 4. Recent Trades
print("=" * 80)
print("4. Recent Trades (Last 10)")
print("=" * 80)
print()

try:
    trades = client.query_trades(limit=10)
    if trades:
        total_trade_value = 0
        print(f"{'Trade ID':<15} {'Symbol':<15} {'Side':<8} {'Qty':<15} {'Price':<15} {'Time':<20}")
        print("-" * 80)
        for trade in trades:
            qty = float(trade.qty) if trade.qty else 0
            price = float(trade.price) if trade.price else 0
            trade_value = qty * price
            total_trade_value += trade_value
            
            trade_time = datetime.fromtimestamp(trade.timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S') if trade.timestamp else 'N/A'
            print(f"{trade.id:<15} {trade.symbol:<15} {trade.side:<8} {qty:<15.8f} ${price:<14.2f} {trade_time:<20}")
        print(f"\nTotal Trades Shown: {len(trades)}")
    else:
        print("No recent trades")
    print()
except Exception as e:
    print(f"Error querying trades: {e}")
    print()

# 5. Portfolio Summary
print("=" * 80)
print("5. Portfolio Summary")
print("=" * 80)
print()

try:
    # Calculate summary statistics
    positions = client.query_positions()
    orders = client.query_open_orders()
    balances = client.query_balances()
    
    total_positions = len(positions) if positions else 0
    total_open_orders = len(orders) if orders else 0
    
    total_realized_pnl = sum(
        float(pos.realized_pnl) if pos.realized_pnl else 0 
        for pos in positions
    ) if positions else 0
    
    total_balance = sum(
        float(bal.total) if bal.total else (
            (float(bal.free) if bal.free else 0) + 
            (float(bal.locked) if bal.locked else 0)
        )
        for bal in balances
    ) if balances else 0
    
    print(f"Total Positions: {total_positions}")
    print(f"Total Open Orders: {total_open_orders}")
    print(f"Total Realized PnL: ${total_realized_pnl:.2f}")
    if total_balance > 0:
        print(f"Total Account Balance: ${total_balance:.2f}")
        if total_balance > 0:
            pnl_percentage = (total_realized_pnl / total_balance) * 100
            print(f"PnL Percentage: {pnl_percentage:.2f}%")
    else:
        print("Total Account Balance: Unable to calculate (balances endpoint may not be available)")
    
    print()
except Exception as e:
    print(f"Error calculating summary: {e}")
    print()

print("=" * 80)
print("Portfolio Overview Complete!")
print("=" * 80)

