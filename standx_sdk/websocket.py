"""WebSocket client for StandX API"""

import json
import uuid
import threading
import time
from typing import Optional, Dict, Any, Callable, List
import websocket
from .auth import StandXAuth
from .exceptions import StandXWebSocketError


class StandXWebSocket:
    """WebSocket client for real-time data streams"""
    
    MARKET_STREAM_URL = "wss://perps.standx.com/ws-stream/v1"
    ORDER_RESPONSE_URL = "wss://perps.standx.com/ws-api/v1"
    
    def __init__(
        self,
        jwt_token: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        session_id: Optional[str] = None,
        on_message: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_close: Optional[Callable] = None
    ):
        """
        Initialize WebSocket client
        
        Args:
            jwt_token: JWT token for authentication
            api_key: API key for order response stream
            api_secret: API secret for order response stream
            session_id: Session ID (must match HTTP client session_id)
            on_message: Callback for received messages
            on_error: Callback for errors
            on_close: Callback for connection close
        """
        self.jwt_token = jwt_token
        self.session_id = session_id or str(uuid.uuid4())
        self.api_key = api_key
        self.api_secret = api_secret
        self.auth = StandXAuth(api_key, api_secret) if api_key and api_secret else None
        
        self.on_message_callback = on_message
        self.on_error_callback = on_error
        self.on_close_callback = on_close
        
        self.ws_market: Optional[websocket.WebSocketApp] = None
        self.ws_order: Optional[websocket.WebSocketApp] = None
        self.connected_market = False
        self.connected_order = False
        
        self._last_ping_time = 0
        self._ping_interval = 10  # seconds
    
    def _on_message_market(self, ws, message):
        """Handle market stream messages"""
        try:
            data = json.loads(message)
            
            # Handle ping/pong
            if isinstance(data, str) and data == "ping":
                ws.send("pong")
                return
            
            if self.on_message_callback:
                self.on_message_callback(data, "market")
        except json.JSONDecodeError:
            if self.on_error_callback:
                self.on_error_callback(f"Invalid JSON: {message}")
    
    def _on_error_market(self, ws, error):
        """Handle market stream errors"""
        if self.on_error_callback:
            self.on_error_callback(f"Market stream error: {error}")
    
    def _on_close_market(self, ws, close_status_code, close_msg):
        """Handle market stream close"""
        self.connected_market = False
        if self.on_close_callback:
            self.on_close_callback("market", close_status_code, close_msg)
    
    def _on_open_market(self, ws):
        """Handle market stream open"""
        self.connected_market = True
        
        # Authenticate if JWT token provided
        if self.jwt_token:
            self.authenticate_market()
    
    def _on_message_order(self, ws, message):
        """Handle order response stream messages"""
        try:
            data = json.loads(message)
            
            if self.on_message_callback:
                self.on_message_callback(data, "order")
        except json.JSONDecodeError:
            if self.on_error_callback:
                self.on_error_callback(f"Invalid JSON: {message}")
    
    def _on_error_order(self, ws, error):
        """Handle order response stream errors"""
        if self.on_error_callback:
            self.on_error_callback(f"Order stream error: {error}")
    
    def _on_close_order(self, ws, close_status_code, close_msg):
        """Handle order response stream close"""
        self.connected_order = False
        if self.on_close_callback:
            self.on_close_callback("order", close_status_code, close_msg)
    
    def _on_open_order(self, ws):
        """Handle order response stream open"""
        self.connected_order = True
        
        # Authenticate if JWT token provided
        if self.jwt_token:
            self.authenticate_order()
    
    def connect_market_stream(self):
        """Connect to market data stream"""
        if self.ws_market and self.connected_market:
            return
        
        self.ws_market = websocket.WebSocketApp(
            self.MARKET_STREAM_URL,
            on_message=self._on_message_market,
            on_error=self._on_error_market,
            on_close=self._on_close_market,
            on_open=self._on_open_market
        )
        
        # Run in separate thread
        thread = threading.Thread(target=self.ws_market.run_forever, daemon=True)
        thread.start()
    
    def connect_order_stream(self):
        """Connect to order response stream"""
        if self.ws_order and self.connected_order:
            return
        
        self.ws_order = websocket.WebSocketApp(
            self.ORDER_RESPONSE_URL,
            on_message=self._on_message_order,
            on_error=self._on_error_order,
            on_close=self._on_close_order,
            on_open=self._on_open_order
        )
        
        # Run in separate thread
        thread = threading.Thread(target=self.ws_order.run_forever, daemon=True)
        thread.start()
    
    def authenticate_market(self, streams: Optional[List[Dict]] = None):
        """
        Authenticate market stream with JWT
        
        Args:
            streams: Optional list of channels to subscribe to immediately
        """
        if not self.jwt_token or not self.ws_market:
            return
        
        auth_msg = {
            "auth": {
                "token": self.jwt_token
            }
        }
        
        if streams:
            auth_msg["auth"]["streams"] = streams
        
        self.ws_market.send(json.dumps(auth_msg))
    
    def authenticate_order(self):
        """Authenticate order response stream with JWT"""
        if not self.jwt_token or not self.ws_order:
            return
        
        request_id = str(uuid.uuid4())
        auth_msg = {
            "session_id": self.session_id,
            "request_id": request_id,
            "method": "auth:login",
            "params": json.dumps({"token": self.jwt_token})
        }
        
        self.ws_order.send(json.dumps(auth_msg))
    
    def subscribe(
        self,
        channel: str,
        symbol: Optional[str] = None
    ):
        """
        Subscribe to a market stream channel
        
        Args:
            channel: Channel name (price, depth_book, order, position, balance, trade)
            symbol: Symbol for symbol-specific channels (optional)
        """
        if not self.ws_market or not self.connected_market:
            raise StandXWebSocketError("Market stream not connected")
        
        subscribe_msg = {
            "subscribe": {
                "channel": channel
            }
        }
        
        if symbol:
            subscribe_msg["subscribe"]["symbol"] = symbol
        
        self.ws_market.send(json.dumps(subscribe_msg))
    
    def create_order_ws(
        self,
        symbol: str,
        side: str,
        order_type: str,
        qty: str,
        time_in_force: str,
        price: Optional[str] = None,
        **kwargs
    ):
        """
        Create order via WebSocket
        
        Args:
            symbol: Trading pair
            side: Order side (buy/sell)
            order_type: Order type (limit/market)
            qty: Order quantity
            time_in_force: Time in force
            price: Order price (for limit orders)
            **kwargs: Additional order parameters
        """
        if not self.ws_order or not self.connected_order:
            raise StandXWebSocketError("Order stream not connected")
        
        if not self.auth:
            raise StandXWebSocketError("API credentials required for order creation")
        
        request_id = str(uuid.uuid4())
        params = {
            "symbol": symbol,
            "side": side,
            "order_type": order_type,
            "qty": qty,
            "time_in_force": time_in_force,
            **kwargs
        }
        
        if price:
            params["price"] = price
        
        params_str = json.dumps(params)
        timestamp = str(int(time.time() * 1000))
        
        # Generate signature
        import hmac
        import hashlib
        import base64
        message = params_str + timestamp
        sig = hmac.new(
            self.auth.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        signature_b64 = base64.b64encode(sig).decode('utf-8')
        
        order_msg = {
            "session_id": self.session_id,
            "request_id": request_id,
            "method": "order:new",
            "header": {
                "x-request-id": request_id,
                "x-request-timestamp": timestamp,
                "x-request-signature": signature_b64
            },
            "params": params_str
        }
        
        self.ws_order.send(json.dumps(order_msg))
        return request_id
    
    def cancel_order_ws(
        self,
        order_id: Optional[int] = None,
        cl_ord_id: Optional[str] = None
    ):
        """
        Cancel order via WebSocket
        
        Args:
            order_id: Order ID
            cl_ord_id: Client order ID
        """
        if not self.ws_order or not self.connected_order:
            raise StandXWebSocketError("Order stream not connected")
        
        if not self.auth:
            raise StandXWebSocketError("API credentials required")
        
        request_id = str(uuid.uuid4())
        params = {}
        if order_id:
            params["order_id"] = order_id
        if cl_ord_id:
            params["cl_ord_id"] = cl_ord_id
        
        params_str = json.dumps(params)
        timestamp = str(int(time.time() * 1000))
        
        # Generate signature
        import hmac
        import hashlib
        import base64
        message = params_str + timestamp
        sig = hmac.new(
            self.auth.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        signature_b64 = base64.b64encode(sig).decode('utf-8')
        
        cancel_msg = {
            "session_id": self.session_id,
            "request_id": request_id,
            "method": "order:cancel",
            "header": {
                "x-request-id": request_id,
                "x-request-timestamp": timestamp,
                "x-request-signature": signature_b64
            },
            "params": params_str
        }
        
        self.ws_order.send(json.dumps(cancel_msg))
        return request_id
    
    def disconnect_market(self):
        """Disconnect market stream"""
        if self.ws_market:
            self.ws_market.close()
            self.connected_market = False
    
    def disconnect_order(self):
        """Disconnect order stream"""
        if self.ws_order:
            self.ws_order.close()
            self.connected_order = False
    
    def disconnect_all(self):
        """Disconnect all streams"""
        self.disconnect_market()
        self.disconnect_order()

