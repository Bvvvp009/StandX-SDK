"""Main StandX API client"""

import json
import requests
from typing import Optional, Dict, Any, List
from .auth import StandXAuth
from .exceptions import StandXAPIError, StandXAuthenticationError, StandXRequestError
from .types import (
    OrderSide,
    OrderType,
    TimeInForce,
    MarginMode,
    Resolution,
)
from .models import (
    OrderResponse,
    StandardResponse,
    Order,
    Trade,
    Position,
    PositionConfig,
    Balance,
    SymbolInfo,
    SymbolMarket,
    SymbolPrice,
    DepthBook,
    RecentTrade,
    FundingRates,
    ServerTime,
    Kline,
    Health,
)


class StandXClient:
    """Main client for interacting with StandX API"""
    
    BASE_URL = "https://perps.standx.com"
    
    def __init__(
        self,
        jwt_token: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        base_url: Optional[str] = None,
        session_id: Optional[str] = None,
        ed25519_private_key: Optional[bytes] = None
    ):
        """
        Initialize StandX client
        
        Args:
            jwt_token: JWT access token for authenticated requests
            api_key: API key (deprecated, kept for backward compatibility)
            api_secret: API secret (deprecated, kept for backward compatibility)
            base_url: Custom base URL (defaults to production)
            session_id: Session ID for order tracking via WebSocket
            ed25519_private_key: ed25519 private key bytes for body signature (auto-generated if None)
        """
        self.jwt_token = jwt_token
        self.base_url = base_url or self.BASE_URL
        self.session_id = session_id
        # Use ed25519 for body signature (per StandX API docs)
        self.auth = StandXAuth(ed25519_private_key=ed25519_private_key)
        
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        signed: bool = False,
        use_jwt: bool = True
    ) -> Dict[str, Any]:
        """
        Make HTTP request to API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            signed: Whether to sign the request
            use_jwt: Whether to use JWT authentication
            
        Returns:
            API response data
            
        Raises:
            StandXAPIError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        # Add authentication
        if signed and self.auth:
            body = json.dumps(data) if data else "{}"
            headers.update(self.auth.generate_signature_headers(body, self.session_id))
            # Signed requests also need JWT token
            if use_jwt and self.jwt_token:
                headers["Authorization"] = f"Bearer {self.jwt_token}"
        elif use_jwt and self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"
        
        # Make request
        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=data if not signed else None,
                data=json.dumps(data) if signed and data else None,
                headers=headers,
                timeout=30
            )
            
            # Handle response
            if response.status_code == 401:
                error_msg = "Authentication failed"
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", error_msg)
                except:
                    error_msg = response.text or error_msg
                raise StandXAuthenticationError(error_msg, 401)
            
            # Get response text before raising for status (to capture error details)
            response_text = response.text
            
            if not response.ok:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", response_text)
                    code = error_data.get("code", response.status_code)
                    request_id = error_data.get("request_id")
                    # Include full error data for debugging
                    if response.status_code in [422, 400]:
                        error_msg = f"{error_msg} | Full response: {json.dumps(error_data)}"
                    raise StandXAPIError(error_msg, code, request_id)
                except json.JSONDecodeError:
                    # If not JSON, raise with text
                    raise StandXRequestError(f"Request failed: {response.status_code} - {response_text}")
                except StandXAPIError:
                    raise  # Re-raise StandXAPIError
            
            response.raise_for_status()
            result = response.json()
            
            # Check API-level errors (only if code field exists and is not 0)
            # Successful responses may not have a code field at all
            if isinstance(result, dict) and result.get("code") is not None and result.get("code") != 0:
                code = result.get("code")
                message = result.get("message", "Unknown error")
                request_id = result.get("request_id")
                raise StandXAPIError(message, code, request_id)
            
            # Handle response - can be dict with data field, or direct list/dict
            if isinstance(result, dict):
                return result.get("data", result)
            else:
                # Direct list or other type
                return result
            
        except requests.exceptions.RequestException as e:
            raise StandXRequestError(f"Request failed: {str(e)}")
        except json.JSONDecodeError:
            raise StandXRequestError("Invalid JSON response")
    
    # Trade Endpoints
    
    def create_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        qty: str,
        time_in_force: TimeInForce,
        price: Optional[str] = None,
        reduce_only: Optional[bool] = None,
        cl_ord_id: Optional[str] = None,
        margin_mode: Optional[MarginMode] = None,
        leverage: Optional[int] = None
    ) -> OrderResponse:
        """
        Create a new order
        
        Args:
            symbol: Trading pair (e.g., "BTC-USD")
            side: Order side (buy/sell)
            order_type: Order type (limit/market)
            qty: Order quantity (as string)
            time_in_force: Time in force (gtc/ioc/alo)
            price: Order price (required for limit orders, as string)
            reduce_only: Only reduce position if true
            cl_ord_id: Client order ID (auto-generated if omitted)
            margin_mode: Margin mode (must match position)
            leverage: Leverage value (must match position)
            
        Returns:
            Order creation response
        """
        data = {
            "symbol": symbol,
            "side": side.value,
            "order_type": order_type.value,
            "qty": qty,
            "time_in_force": time_in_force.value,
            "reduce_only": reduce_only if reduce_only is not None else False,  # Required field
        }
        
        if price:
            data["price"] = price
        if cl_ord_id:
            data["cl_ord_id"] = cl_ord_id
        if margin_mode:
            data["margin_mode"] = margin_mode.value
        if leverage:
            data["leverage"] = leverage
        
        result = self._request("POST", "/api/new_order", data=data, signed=True)
        if isinstance(result, dict):
            return OrderResponse(
                code=result.get("code", 0),
                message=result.get("message", "success"),
                request_id=result.get("request_id"),
                order_id=result.get("order_id"),
                cl_ord_id=result.get("cl_ord_id")
            )
        return OrderResponse(code=0, message="success")
    
    def cancel_order(
        self,
        order_id: Optional[int] = None,
        cl_ord_id: Optional[str] = None
    ) -> OrderResponse:
        """
        Cancel an order
        
        Args:
            order_id: Order ID to cancel
            cl_ord_id: Client order ID to cancel
            
        Returns:
            Cancellation response
        """
        if not order_id and not cl_ord_id:
            raise ValueError("Either order_id or cl_ord_id must be provided")
        
        data = {}
        if order_id:
            data["order_id"] = order_id
        if cl_ord_id:
            data["cl_ord_id"] = cl_ord_id
        
        result = self._request("POST", "/api/cancel_order", data=data, signed=True)
        if isinstance(result, dict):
            return OrderResponse(
                code=result.get("code", 0),
                message=result.get("message", "success"),
                request_id=result.get("request_id")
            )
        return OrderResponse(code=0, message="success")
    
    def cancel_orders(
        self,
        order_id_list: Optional[List[int]] = None,
        cl_ord_id_list: Optional[List[str]] = None
    ) -> List[OrderResponse]:
        """
        Cancel multiple orders
        
        Args:
            order_id_list: List of order IDs to cancel
            cl_ord_id_list: List of client order IDs to cancel
            
        Returns:
            List of cancellation results
        """
        if not order_id_list and not cl_ord_id_list:
            raise ValueError("Either order_id_list or cl_ord_id_list must be provided")
        
        data = {}
        if order_id_list:
            data["order_id_list"] = order_id_list
        if cl_ord_id_list:
            data["cl_ord_id_list"] = cl_ord_id_list
        
        result = self._request("POST", "/api/cancel_orders", data=data, signed=True)
        if isinstance(result, list):
            return [
                OrderResponse(
                    code=item.get("code", 0) if isinstance(item, dict) else 0,
                    message=item.get("message", "success") if isinstance(item, dict) else "success",
                    request_id=item.get("request_id") if isinstance(item, dict) else None
                )
                for item in result
            ]
        return []
    
    def change_leverage(self, symbol: str, leverage: int) -> StandardResponse:
        """
        Change position leverage
        
        Args:
            symbol: Trading pair
            leverage: New leverage value
            
        Returns:
            Response data
        """
        data = {"symbol": symbol, "leverage": leverage}
        result = self._request("POST", "/api/change_leverage", data=data, signed=True)
        if isinstance(result, dict):
            return StandardResponse(
                code=result.get("code", 0),
                message=result.get("message", "success"),
                request_id=result.get("request_id")
            )
        return StandardResponse(code=0, message="success")
    
    def change_margin_mode(
        self,
        symbol: str,
        margin_mode: MarginMode
    ) -> StandardResponse:
        """
        Change margin mode
        
        Args:
            symbol: Trading pair
            margin_mode: New margin mode (cross/isolated)
            
        Returns:
            Response data
        """
        data = {"symbol": symbol, "margin_mode": margin_mode.value}
        result = self._request("POST", "/api/change_margin_mode", data=data, signed=True)
        if isinstance(result, dict):
            return StandardResponse(
                code=result.get("code", 0),
                message=result.get("message", "success"),
                request_id=result.get("request_id")
            )
        return StandardResponse(code=0, message="success")
    
    def transfer_margin(
        self,
        symbol: str,
        amount_in: str,
        direction: str = "add"
    ) -> StandardResponse:
        """
        Transfer margin to/from position
        
        Args:
            symbol: Trading pair
            amount_in: Amount to transfer (as string)
            direction: "add" or "remove"
            
        Returns:
            Response data
        """
        data = {
            "symbol": symbol,
            "amount_in": amount_in,
            "direction": direction
        }
        result = self._request("POST", "/api/transfer_margin", data=data, signed=True)
        if isinstance(result, dict):
            return StandardResponse(
                code=result.get("code", 0),
                message=result.get("message", "success"),
                request_id=result.get("request_id")
            )
        return StandardResponse(code=0, message="success")
    
    # User Query Endpoints
    
    def query_order(
        self,
        symbol: str,
        order_id: Optional[int] = None,
        cl_ord_id: Optional[str] = None
    ) -> Order:
        """
        Query order details
        
        Args:
            symbol: Trading pair
            order_id: Order ID
            cl_ord_id: Client order ID
            
        Returns:
            Order object
        """
        params = {"symbol": symbol}
        if order_id:
            params["order_id"] = order_id
        if cl_ord_id:
            params["cl_ord_id"] = cl_ord_id
        
        data = self._request("GET", "/api/query_order", params=params)
        return Order.from_dict(data)
    
    def query_orders(
        self,
        symbol: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Order]:
        """
        Query user orders
        
        Args:
            symbol: Trading pair (optional)
            status: Order status (optional)
            limit: Number of results (optional)
            offset: Offset for pagination (optional)
            
        Returns:
            List of Order objects
        """
        params = {}
        if symbol:
            params["symbol"] = symbol
        if status:
            params["status"] = status
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
        
        data = self._request("GET", "/api/query_orders", params=params)
        return [Order.from_dict(order) for order in data] if isinstance(data, list) else []
    
    def query_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """
        Query all open orders
        
        Args:
            symbol: Trading pair (optional)
            
        Returns:
            List of open Order objects
        """
        params = {}
        if symbol:
            params["symbol"] = symbol
        
        data = self._request("GET", "/api/query_open_orders", params=params)
        return [Order.from_dict(order) for order in data] if isinstance(data, list) else []
    
    def query_trades(
        self,
        symbol: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Trade]:
        """
        Query user trades
        
        Args:
            symbol: Trading pair (optional)
            limit: Number of results (optional)
            offset: Offset for pagination (optional)
            
        Returns:
            List of trade data
        """
        params = {}
        if symbol:
            params["symbol"] = symbol
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
        
        data = self._request("GET", "/api/query_trades", params=params)
        return [Trade.from_dict(trade) for trade in data] if isinstance(data, list) else []
    
    def query_position_config(self, symbol: str) -> PositionConfig:
        """
        Query position configuration
        
        Args:
            symbol: Trading pair
            
        Returns:
            Position configuration data
        """
        data = self._request("GET", "/api/query_position_config", params={"symbol": symbol})
        return PositionConfig.from_dict(data) if isinstance(data, dict) else PositionConfig()
    
    def query_positions(self, symbol: Optional[str] = None) -> List[Position]:
        """
        Query user positions
        
        Args:
            symbol: Trading pair (optional)
            
        Returns:
            List of Position objects
        """
        params = {}
        if symbol:
            params["symbol"] = symbol
        
        data = self._request("GET", "/api/query_positions", params=params)
        return [Position.from_dict(pos) for pos in data] if isinstance(data, list) else []
    
    def query_balances(self) -> List[Balance]:
        """
        Query user balances
        
        Returns:
            List of Balance objects
        """
        data = self._request("GET", "/api/query_user_balances")
        return [Balance.from_dict(bal) for bal in data] if isinstance(data, list) else []
    
    # Public Endpoints
    
    def query_symbol_info(self, symbol: Optional[str] = None) -> SymbolInfo:
        """
        Query symbol information
        
        Args:
            symbol: Trading pair (optional, returns all if omitted)
            
        Returns:
            Symbol information
        """
        params = {}
        if symbol:
            params["symbol"] = symbol
        
        data = self._request("GET", "/api/query_symbol_info", params=params, use_jwt=False)
        return SymbolInfo.from_dict(data) if isinstance(data, dict) else SymbolInfo()
    
    def query_symbol_market(self, symbol: str) -> SymbolMarket:
        """
        Query symbol market data
        
        Args:
            symbol: Trading pair
            
        Returns:
            Market data
        """
        data = self._request("GET", "/api/query_symbol_market", params={"symbol": symbol}, use_jwt=False)
        return SymbolMarket.from_dict(data) if isinstance(data, dict) else SymbolMarket()
    
    def query_symbol_price(self, symbol: str) -> SymbolPrice:
        """
        Query symbol price
        
        Args:
            symbol: Trading pair
            
        Returns:
            Price data
        """
        data = self._request("GET", "/api/query_symbol_price", params={"symbol": symbol}, use_jwt=False)
        return SymbolPrice.from_dict(data) if isinstance(data, dict) else SymbolPrice()
    
    def query_depth_book(
        self,
        symbol: str,
        limit: Optional[int] = None
    ) -> DepthBook:
        """
        Query order book depth
        
        Args:
            symbol: Trading pair
            limit: Number of levels (optional, default: 100)
            
        Returns:
            Order book data
        """
        params = {"symbol": symbol}
        if limit:
            params["limit"] = limit
        
        data = self._request("GET", "/api/query_depth_book", params=params, use_jwt=False)
        return DepthBook.from_dict(data) if isinstance(data, dict) else DepthBook()
    
    def query_recent_trades(
        self,
        symbol: str,
        limit: Optional[int] = None
    ) -> List[RecentTrade]:
        """
        Query recent trades
        
        Args:
            symbol: Trading pair
            limit: Number of results (optional, default: 100)
            
        Returns:
            List of recent trades
        """
        params = {"symbol": symbol}
        if limit:
            params["limit"] = limit
        
        data = self._request("GET", "/api/query_recent_trades", params=params, use_jwt=False)
        return [RecentTrade.from_dict(trade) for trade in data] if isinstance(data, list) else []
    
    def query_funding_rates(self, symbol: Optional[str] = None) -> FundingRates:
        """
        Query funding rates
        
        Args:
            symbol: Trading pair (optional)
            
        Returns:
            Funding rate data
        """
        params = {}
        if symbol:
            params["symbol"] = symbol
        
        data = self._request("GET", "/api/query_funding_rates", params=params, use_jwt=False)
        return FundingRates.from_dict(data) if isinstance(data, dict) else FundingRates()
    
    # Kline Endpoints
    
    def get_server_time(self) -> ServerTime:
        """
        Get server time
        
        Returns:
            Server time data
        """
        data = self._request("GET", "/api/kline/time", use_jwt=False)
        return ServerTime.from_dict(data) if isinstance(data, dict) else ServerTime()
    
    def get_kline_history(
        self,
        symbol: str,
        resolution: Resolution,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[Kline]:
        """
        Get kline/candlestick history
        
        Args:
            symbol: Trading pair
            resolution: Kline resolution
            from_time: Start timestamp (optional)
            to_time: End timestamp (optional)
            limit: Number of results (optional, default: 500)
            
        Returns:
            List of kline data
        """
        params = {
            "symbol": symbol,
            "resolution": resolution.value
        }
        if from_time:
            params["from"] = from_time
        if to_time:
            params["to"] = to_time
        if limit:
            params["limit"] = limit
        
        data = self._request("GET", "/api/kline/history", params=params, use_jwt=False)
        return [Kline.from_dict(kline) for kline in data] if isinstance(data, list) else []
    
    # Health Check
    
    def health(self) -> Health:
        """
        Health check endpoint
        
        Returns:
            Health status
        """
        data = self._request("GET", "/api/health", use_jwt=False)
        return Health.from_dict(data) if isinstance(data, dict) else Health()
    
    # Misc Endpoints
    
    def get_region_and_server_time(self) -> Dict[str, Any]:
        """
        Get region and server time
        
        Returns:
            Region and server time data
        """
        return self._request("GET", "/api/region_and_server_time", use_jwt=False)

