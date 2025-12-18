"""Convenience client that generates credentials from wallet private key"""

import hashlib
from typing import Optional
from .client import StandXClient
from .wallet_auth import StandXWalletAuth


class StandXWalletClient(StandXClient):
    """
    StandX client that automatically generates JWT token and API credentials from wallet private key
    
    This eliminates the need to manually obtain credentials from the platform.
    API credentials are automatically generated from the private key for trading.
    """
    
    @staticmethod
    def _generate_api_credentials_from_private_key(private_key: str, wallet_address: str) -> tuple[str, str]:
        """
        Generate deterministic API credentials from private key
        
        Args:
            private_key: Wallet private key (hex string)
            wallet_address: Wallet address
            
        Returns:
            Tuple of (api_key, api_secret)
        """
        # Remove 0x prefix if present
        private_key_clean = private_key.replace("0x", "")
        
        # Generate API key from wallet address (deterministic)
        api_key = wallet_address.lower()
        
        # Generate API secret from private key (deterministic)
        # Use HMAC-SHA256 of a seed string with private key
        seed = f"standx_api_secret_{wallet_address.lower()}"
        api_secret = hashlib.sha256(f"{seed}{private_key_clean}".encode()).hexdigest()
        
        return api_key, api_secret
    
    def __init__(
        self,
        private_key: Optional[str] = None,
        wallet_address: Optional[str] = None,
        chain: str = "bsc",
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        base_url: Optional[str] = None,
        session_id: Optional[str] = None,
        expires_seconds: int = 604800,
        auto_generate_api_credentials: bool = True,
        jwt_token: Optional[str] = None
    ):
        """
        Initialize StandX client with wallet private key
        
        Args:
            private_key: Wallet private key (hex string). If None, will try to use from .env
            wallet_address: Wallet address (optional, will derive if not provided)
            chain: Blockchain network ("bsc" or "solana")
            api_key: API key for trading endpoints (deprecated, not needed with ed25519)
            api_secret: API secret for trading endpoints (deprecated, not needed with ed25519)
            base_url: Custom base URL
            session_id: Session ID for order tracking
            expires_seconds: JWT token expiration time (default: 7 days) - only used if generating new token
            auto_generate_api_credentials: If True, generate API credentials from private key if not provided
            jwt_token: JWT token to use. If None, will generate from private_key or use from .env
        """
        import os
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        
        # Get private key from parameter or environment
        if not private_key:
            private_key = os.getenv("STANDX_PRIVATE_KEY")
            if not private_key:
                raise ValueError("private_key is required. Provide it directly or set STANDX_PRIVATE_KEY in .env")
        
        # Get chain from environment if not provided
        if chain == "bsc" and os.getenv("STANDX_CHAIN"):
            chain = os.getenv("STANDX_CHAIN")
        
        # Derive wallet address first (needed for JWT generation or verification)
        if not wallet_address:
            wallet_address = os.getenv("STANDX_WALLET_ADDRESS")
        if not wallet_address and chain in ["bsc", "ethereum"]:
            from eth_account import Account
            account = Account.from_key(private_key)
            wallet_address = account.address
        
        # Always generate JWT token from private key to ensure it's valid and fresh
        # This ensures we have the matching ed25519 key pair for body signature
        # Per StandX API docs: ed25519 key pair is temporary and generated per session
        auth = StandXWalletAuth(chain=chain)
        
        # Get JWT token (this also generates and stores ed25519 key pair)
        jwt_token_to_use = auth.get_jwt_token(
            wallet_address=wallet_address,
            private_key=private_key,
            chain=chain,
            expires_seconds=expires_seconds
        )
        
        # Use the SAME ed25519 key pair that was used for JWT authentication
        # This is the temporary ed25519 key pair per StandX API docs
        ed25519_private_key_bytes = auth._ed25519_private_key_bytes
        
        if not ed25519_private_key_bytes:
            # Fallback: generate new one if not available
            from cryptography.hazmat.primitives.asymmetric import ed25519
            temp_key = ed25519.Ed25519PrivateKey.generate()
            ed25519_private_key_bytes = temp_key.private_bytes_raw()
        
        # Initialize parent client with JWT and ed25519 auth
        super().__init__(
            jwt_token=jwt_token_to_use,
            api_key=None,  # Not needed - using ed25519
            api_secret=None,  # Not needed - using ed25519
            base_url=base_url,
            session_id=session_id,
            ed25519_private_key=ed25519_private_key_bytes
        )
        
        self.wallet_address = wallet_address
        self.chain = chain
        self._auto_generated_credentials = auto_generate_api_credentials and (not api_key or not api_secret)







