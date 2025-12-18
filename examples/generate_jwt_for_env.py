"""Generate JWT Token for .env File

This example generates a JWT token from your private key and displays
instructions for adding it to your .env file.

Note: StandXWalletClient auto-generates JWT tokens, so you typically
don't need to run this. This is useful if you want to reuse a JWT token
or use StandXClient directly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from standx_sdk.wallet_auth import StandXWalletAuth
from eth_account import Account

print("=" * 70)
print("Generate JWT Token for .env File")
print("=" * 70)

# Get private key from environment
private_key = os.getenv("STANDX_PRIVATE_KEY")
chain = os.getenv("STANDX_CHAIN", "bsc")

if not private_key:
    print("\n[ERROR] STANDX_PRIVATE_KEY not found in .env file")
    print("\nPlease add your private key to .env file:")
    print("STANDX_PRIVATE_KEY=0x_your_private_key_here")
    sys.exit(1)

# Derive wallet address
if chain in ["bsc", "ethereum"]:
    account = Account.from_key(private_key)
    wallet_address = account.address
else:
    print(f"[ERROR] Chain {chain} not supported for address derivation")
    sys.exit(1)

print(f"\nWallet Address: {wallet_address}")
print(f"Chain: {chain}")
print(f"Private Key: {'*' * 20}...{private_key[-8:]}")

# Generate JWT token
print("\n" + "=" * 70)
print("Generating JWT Token...")
print("=" * 70)

try:
    auth = StandXWalletAuth(chain=chain)
    jwt_token = auth.get_jwt_token(
        wallet_address=wallet_address,
        private_key=private_key,
        chain=chain,
        expires_seconds=604800  # 7 days
    )
    
    print("\n[SUCCESS] JWT token generated!")
    print(f"\nToken Length: {len(jwt_token)} characters")
    print(f"Token Preview: {jwt_token[:50]}...{jwt_token[-20:]}")
    
    # Display instructions for .env file
    print("\n" + "=" * 70)
    print("Add this to your .env file:")
    print("=" * 70)
    print("\n# StandX API Credentials")
    print(f"STANDX_PRIVATE_KEY={private_key}")
    print(f"STANDX_CHAIN={chain}")
    print(f"STANDX_JWT_TOKEN={jwt_token}")
    print("\n# Optional: Wallet address (auto-derived if not provided)")
    print(f"STANDX_WALLET_ADDRESS={wallet_address}")
    
    print("\n" + "=" * 70)
    print("Note:")
    print("=" * 70)
    print("- JWT tokens expire after 7 days by default")
    print("- You can regenerate a new token anytime using this script")
    print("- The token is used for authenticated API requests")
    print("- Keep your private key secure and never share it")
    
    # Verify token works
    print("\n" + "=" * 70)
    print("Verifying token...")
    print("=" * 70)
    
    from standx_sdk import StandXClient
    test_client = StandXClient(jwt_token=jwt_token)
    try:
        price = test_client.query_symbol_price("BTC-USD")
        print(f"[OK] Token verified! BTC Price: ${price.last_price}")
        print("\n[SUCCESS] Your JWT token is valid and ready to use!")
    except Exception as e:
        print(f"[WARNING] Token verification failed: {e}")
        print("The token may still be valid, but there was an issue testing it.")
    
except Exception as e:
    print(f"\n[ERROR] Failed to generate JWT token: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("Done!")
print("=" * 70)



