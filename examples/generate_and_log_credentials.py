"""Generate and Log All Credentials for StandX API

This example generates all necessary credentials from a private key and logs them
in a format that can be used in other examples. It demonstrates:
- JWT token generation
- Wallet address derivation
- Credential logging and formatting
- Credential validation

Run this first to generate credentials, then use them in other examples.
"""

import sys
import os
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from standx_sdk.wallet_auth import StandXWalletAuth
from eth_account import Account
from standx_sdk import StandXWalletClient

print("=" * 80)
print("StandX API Credential Generator")
print("=" * 80)
print()

# Get private key from environment
private_key = os.getenv("STANDX_PRIVATE_KEY")
chain = os.getenv("STANDX_CHAIN", "bsc")

if not private_key:
    print("[ERROR] STANDX_PRIVATE_KEY not found in .env file")
    print("\nPlease add your private key to .env file:")
    print("STANDX_PRIVATE_KEY=0x_your_private_key_here")
    print("STANDX_CHAIN=bsc  # or ethereum, solana")
    sys.exit(1)

# Derive wallet address
print("Step 1: Deriving wallet address...")
if chain in ["bsc", "ethereum"]:
    account = Account.from_key(private_key)
    wallet_address = account.address
    print(f"  [OK] Wallet Address: {wallet_address}")
elif chain == "solana":
    print(f"[ERROR] Solana address derivation not implemented yet")
    sys.exit(1)
else:
    print(f"[ERROR] Chain {chain} not supported")
    sys.exit(1)

print(f"  [OK] Chain: {chain}")
print(f"  [OK] Private Key: {'*' * 20}...{private_key[-8:]}")
print()

# Generate JWT token
print("Step 2: Generating JWT token...")
try:
    auth = StandXWalletAuth(chain=chain)
    jwt_token = auth.get_jwt_token(
        wallet_address=wallet_address,
        private_key=private_key,
        chain=chain,
        expires_seconds=604800  # 7 days
    )
    
    print(f"  [OK] JWT Token Generated")
    print(f"  [OK] Token Length: {len(jwt_token)} characters")
    print(f"  [OK] Token Preview: {jwt_token[:50]}...{jwt_token[-20:]}")
    print()
    
    # Get ed25519 keys info
    ed25519_private_key_bytes = auth._ed25519_private_key_bytes
    if ed25519_private_key_bytes:
        print("Step 3: ed25519 Key Pair (for body signatures)...")
        print(f"  [OK] Private Key Bytes Length: {len(ed25519_private_key_bytes)}")
        print(f"  [OK] Private Key Hex: {ed25519_private_key_bytes.hex()[:50]}...")
        print()
    
    # Initialize client to verify credentials work
    print("Step 4: Verifying credentials...")
    client = StandXWalletClient(
        private_key=private_key,
        chain=chain
    )
    
    # Test public endpoint
    try:
        price = client.query_symbol_price("BTC-USD")
        print(f"  [OK] Public API Access: OK")
        print(f"  [OK] BTC Price: ${price.last_price}")
    except Exception as e:
        print(f"  [ERROR] Public API Access Failed: {e}")
    
    # Test authenticated endpoint
    try:
        positions = client.query_positions()
        print(f"  [OK] Authenticated API Access: OK")
        print(f"  [OK] Positions Count: {len(positions)}")
    except Exception as e:
        print(f"  [ERROR] Authenticated API Access Failed: {e}")
    
    print()
    
    # Log all credentials in a structured format
    print("=" * 80)
    print("CREDENTIALS SUMMARY")
    print("=" * 80)
    print()
    
    credentials = {
        "wallet_address": wallet_address,
        "chain": chain,
        "jwt_token": jwt_token,
        "private_key_masked": f"{'*' * 20}...{private_key[-8:]}",
        "generated_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(seconds=604800)).isoformat(),
        "ed25519_private_key_hex": ed25519_private_key_bytes.hex() if ed25519_private_key_bytes else None
    }
    
    print("JSON Format (for programmatic use):")
    print("-" * 80)
    print(json.dumps(credentials, indent=2))
    print()
    
    print("Environment Variables Format (for .env file):")
    print("-" * 80)
    print(f"STANDX_WALLET_ADDRESS={wallet_address}")
    print(f"STANDX_CHAIN={chain}")
    print(f"STANDX_JWT_TOKEN={jwt_token}")
    print(f"STANDX_PRIVATE_KEY={private_key[:10]}...{private_key[-8:]}  # MASKED - use your actual key from .env")
    if ed25519_private_key_bytes:
        ed25519_hex = ed25519_private_key_bytes.hex()
        print(f"STANDX_ED25519_PRIVATE_KEY={ed25519_hex[:10]}...{ed25519_hex[-8:]}  # MASKED - auto-generated, not needed")
    print()
    print("Note: The actual private key is already in your .env file.")
    print("You don't need to copy these values - StandXWalletClient uses STANDX_PRIVATE_KEY directly.")
    print()
    
    print("Python Dictionary Format (for direct use in code):")
    print("-" * 80)
    print("credentials = {")
    print(f'    "wallet_address": "{wallet_address}",')
    print(f'    "chain": "{chain}",')
    print(f'    "jwt_token": "{jwt_token}",')
    print(f'    "private_key": "***MASKED***",  # Use os.getenv("STANDX_PRIVATE_KEY") instead')
    if ed25519_private_key_bytes:
        print(f'    "ed25519_private_key_hex": "***MASKED***",  # Auto-generated, not needed')
    print("}")
    print()
    
    # Save to file in examples directory
    examples_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(examples_dir, "generated_credentials.json")
    with open(output_file, "w") as f:
        json.dump(credentials, f, indent=2)
    print(f"[OK] Credentials saved to: {output_file}")
    print()
    
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()
    print("You can now use these credentials in other examples:")
    print("  1. Set them in your .env file (recommended)")
    print("  2. Load from generated_credentials.json file")
    print("  3. Pass directly to StandXWalletClient or StandXClient")
    print()
    print("Example usage:")
    print("  from standx_sdk import StandXWalletClient")
    print("  import os")
    print("  from dotenv import load_dotenv")
    print("  load_dotenv()")
    print("  client = StandXWalletClient(private_key=os.getenv('STANDX_PRIVATE_KEY'))")
    print()
    
except Exception as e:
    print(f"\n[ERROR] Failed to generate credentials: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 80)
print("Done!")
print("=" * 80)

