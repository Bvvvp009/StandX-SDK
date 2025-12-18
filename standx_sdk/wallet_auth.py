"""Wallet-based authentication for StandX API

This module provides functionality to generate JWT tokens from wallet private keys,
eliminating the need to manually obtain credentials from the platform.
"""

import json
import base64
import base58
import requests
from typing import Optional, Dict, Any
from eth_account import Account
from eth_account.messages import encode_defunct
import hashlib
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


class StandXWalletAuth:
    """Generate StandX credentials from wallet private key"""
    
    AUTH_BASE_URL = "https://api.standx.com/v1/offchain"
    
    def __init__(self, chain: str = "bsc"):
        """
        Initialize wallet authentication
        
        Args:
            chain: Blockchain network ("bsc" or "solana")
        """
        self.chain = chain
        self.auth_base_url = self.AUTH_BASE_URL
        self._ed25519_private_key_bytes = None  # Will be set during JWT token generation
    
    def generate_request_id(self) -> tuple[str, bytes]:
        """
        Generate requestId (base58-encoded ed25519 public key) and return private key
        
        Returns:
            Tuple of (base58-encoded public key string, ed25519 private key bytes)
        """
        # Generate ed25519 key pair
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        # Serialize public key
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        # Get private key bytes
        private_key_bytes = private_key.private_bytes_raw()
        
        # Encode to base58
        request_id = base58.b58encode(public_key_bytes).decode('utf-8')
        return request_id, private_key_bytes
    
    def get_signature_data(
        self,
        wallet_address: str,
        request_id: str
    ) -> Dict[str, Any]:
        """
        Get signature data from StandX API
        
        Args:
            wallet_address: Your wallet address
            request_id: Base58-encoded public key from generate_request_id()
            
        Returns:
            Dictionary containing signedData (JWT string)
            
        Raises:
            StandXAPIError: If request fails
        """
        url = f"{self.auth_base_url}/prepare-signin"
        params = {"chain": self.chain}
        
        data = {
            "address": wallet_address,
            "requestId": request_id
        }
        
        response = requests.post(
            url,
            params=params,
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        response.raise_for_status()
        result = response.json()
        
        if not result.get("success"):
            raise Exception(f"Failed to get signature data: {result}")
        
        return result
    
    def sign_message_ethereum(
        self,
        private_key: str,
        message: str
    ) -> str:
        """
        Sign message with Ethereum private key
        
        Args:
            private_key: Ethereum private key (hex string with or without 0x)
            message: Message to sign
            
        Returns:
            Signature hex string with 0x prefix (required by StandX API)
        """
        # Remove 0x prefix if present
        if private_key.startswith("0x"):
            private_key = private_key[2:]
        
        # Create account from private key
        account = Account.from_key(private_key)
        
        # Encode message
        message_encoded = encode_defunct(text=message)
        
        # Sign message
        signed_message = account.sign_message(message_encoded)
        
        # Return signature with 0x prefix (required by StandX API)
        return "0x" + signed_message.signature.hex()
    
    def sign_message_solana(
        self,
        private_key: bytes,
        message: str
    ) -> str:
        """
        Sign message with Solana private key
        
        Args:
            private_key: Solana private key bytes (32 bytes)
            message: Message to sign
            
        Returns:
            Base64-encoded signature
        """
        # Create ed25519 key from private key
        private_key_obj = ed25519.Ed25519PrivateKey.from_private_bytes(private_key)
        
        # Sign message
        signature = private_key_obj.sign(message.encode('utf-8'))
        
        # Return base64-encoded signature
        return base64.b64encode(signature).decode('utf-8')
    
    def get_jwt_token(
        self,
        wallet_address: str,
        private_key: str,
        chain: Optional[str] = None,
        expires_seconds: int = 604800
    ) -> str:
        """
        Get JWT token from wallet private key (complete flow)
        
        Args:
            wallet_address: Your wallet address
            private_key: Private key (hex string for Ethereum, bytes for Solana)
            chain: Blockchain network ("bsc" or "solana"), defaults to self.chain
            expires_seconds: Token expiration time in seconds (default: 7 days)
            
        Returns:
            JWT access token
            
        Raises:
            Exception: If authentication fails
        """
        chain = chain or self.chain
        
        # Step 1: Generate requestId and ed25519 key pair
        request_id, ed25519_private_key_bytes = self.generate_request_id()
        
        # Store ed25519 private key for later use in body signature
        self._ed25519_private_key_bytes = ed25519_private_key_bytes
        
        # Step 2: Get signature data
        sig_data_response = self.get_signature_data(wallet_address, request_id)
        signed_data = sig_data_response["signedData"]
        
        # Step 3: Parse signedData (JWT) to get message
        # JWT format: header.payload.signature
        # We need to decode the payload to get the message
        try:
            import jwt
            # Decode without verification to get payload
            payload = jwt.decode(signed_data, options={"verify_signature": False})
            message = payload.get("message", "")
        except ImportError:
            # Fallback: manually parse JWT
            parts = signed_data.split('.')
            if len(parts) != 3:
                raise Exception("Invalid signedData format")
            
            # Decode payload (base64url)
            payload_b64 = parts[1]
            # Add padding if needed
            payload_b64 += '=' * (4 - len(payload_b64) % 4)
            payload_json = base64.urlsafe_b64decode(payload_b64)
            payload = json.loads(payload_json)
            message = payload.get("message", "")
        
        # Step 4: Sign the message
        if chain in ["bsc", "ethereum"]:
            signature = self.sign_message_ethereum(private_key, message)
        elif chain == "solana":
            if isinstance(private_key, str):
                # Convert hex string to bytes
                if private_key.startswith("0x"):
                    private_key = private_key[2:]
                private_key = bytes.fromhex(private_key)
            signature = self.sign_message_solana(private_key, message)
        else:
            raise ValueError(f"Unsupported chain: {chain}")
        
        # Step 5: Get access token
        url = f"{self.auth_base_url}/login"
        params = {"chain": chain}
        
        data = {
            "signature": signature,
            "signedData": signed_data,
            "expiresSeconds": expires_seconds
        }
        
        response = requests.post(
            url,
            params=params,
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Check if we have a token in the response
        token = result.get("token") or result.get("accessToken") or result.get("jwt")
        
        if not token:
            # If no token but response was successful, check if success field indicates failure
            if result.get("success") is False:
                raise Exception(f"Failed to get JWT token: {result}")
            # Some responses may not have success field but still contain token
            raise Exception(f"No token in response: {result}")
        
        return token
    
    @staticmethod
    def from_private_key(
        private_key: str,
        wallet_address: Optional[str] = None,
        chain: str = "bsc"
    ) -> Dict[str, str]:
        """
        Convenience method to get JWT token from private key
        
        Args:
            private_key: Private key (hex string)
            wallet_address: Wallet address (optional, will derive if not provided)
            chain: Blockchain network ("bsc" or "solana")
            
        Returns:
            Dictionary with jwt_token
        """
        auth = StandXWalletAuth(chain=chain)
        
        # Derive address if not provided (for Ethereum/BSC)
        if not wallet_address and chain in ["bsc", "ethereum"]:
            from eth_account import Account
            account = Account.from_key(private_key)
            wallet_address = account.address
        
        jwt_token = auth.get_jwt_token(wallet_address, private_key, chain)
        
        return {
            "jwt_token": jwt_token,
            "wallet_address": wallet_address
        }


# Note: API Key and Secret still need to be obtained from platform
# These are separate from wallet authentication and are used for body signature
# They may be generated/assigned during account setup on the platform

