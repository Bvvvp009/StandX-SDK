"""Authentication and signature generation for StandX API"""

import base64
import uuid
import time
from typing import Dict, Optional
from cryptography.hazmat.primitives.asymmetric import ed25519


class StandXAuth:
    """Handles authentication and request signing for StandX API using ed25519"""
    
    def __init__(self, ed25519_private_key: Optional[bytes] = None):
        """
        Initialize authentication with ed25519 key pair
        
        Args:
            ed25519_private_key: ed25519 private key bytes (32 bytes). If None, generates a new key pair.
        """
        if ed25519_private_key is None:
            # Generate new ed25519 key pair
            self._ed25519_private_key = ed25519.Ed25519PrivateKey.generate()
        else:
            # Use provided private key
            self._ed25519_private_key = ed25519.Ed25519PrivateKey.from_private_bytes(ed25519_private_key)
        
        self._ed25519_public_key = self._ed25519_private_key.public_key()
    
    @property
    def ed25519_private_key(self) -> bytes:
        """Get ed25519 private key bytes"""
        return self._ed25519_private_key.private_bytes_raw()
    
    @property
    def ed25519_public_key(self) -> bytes:
        """Get ed25519 public key bytes"""
        return self._ed25519_public_key.public_bytes_raw()
    
    def generate_signature_headers(
        self,
        body: str,
        session_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate signature headers for authenticated requests using ed25519
        
        According to StandX API docs: https://docs.standx.com/standx-api/perps-auth#body-signature-flow
        Message format: {version},{id},{timestamp},{payload}
        
        Args:
            body: JSON stringified request body (payload)
            session_id: Optional session ID for order tracking
            
        Returns:
            Dictionary of headers to include in the request
        """
        version = "v1"
        request_id = str(uuid.uuid4())  # Use UUID as requestId (per StandX API docs example)
        timestamp = int(time.time() * 1000)
        
        # Build message to sign: "{version},{id},{timestamp},{payload}"
        message = f"{version},{request_id},{timestamp},{body}"
        
        # Sign message with ed25519 private key
        message_bytes = message.encode('utf-8')
        signature = self._ed25519_private_key.sign(message_bytes)
        
        # Base64 encode the signature
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        headers = {
            "x-request-sign-version": version,
            "x-request-id": request_id,
            "x-request-timestamp": str(timestamp),
            "x-request-signature": signature_b64,
            "Content-Type": "application/json",
        }
        
        if session_id:
            headers["x-session-id"] = session_id
        
        return headers
    
    def get_jwt_headers(self, jwt_token: str) -> Dict[str, str]:
        """
        Get headers for JWT-authenticated requests
        
        Args:
            jwt_token: JWT access token
            
        Returns:
            Dictionary of headers to include in the request
        """
        return {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json",
        }











