"""
StandX API Python SDK

A comprehensive Python SDK for interacting with the StandX Perpetual Futures API.
"""

from .client import StandXClient
from .wallet_client import StandXWalletClient
from .wallet_auth import StandXWalletAuth
from .websocket import StandXWebSocket
from .exceptions import (
    StandXAPIError,
    StandXAuthenticationError,
    StandXRequestError,
    StandXWebSocketError,
)
from .types import (
    OrderSide,
    OrderType,
    OrderStatus,
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

__version__ = "1.0.0"
__all__ = [
    "StandXClient",
    "StandXWalletClient",
    "StandXWalletAuth",
    "StandXWebSocket",
    "StandXAPIError",
    "StandXAuthenticationError",
    "StandXRequestError",
    "StandXWebSocketError",
    "OrderSide",
    "OrderType",
    "OrderStatus",
    "TimeInForce",
    "MarginMode",
    "Resolution",
    "OrderResponse",
    "StandardResponse",
    "Order",
    "Trade",
    "Position",
    "PositionConfig",
    "Balance",
    "SymbolInfo",
    "SymbolMarket",
    "SymbolPrice",
    "DepthBook",
    "RecentTrade",
    "FundingRates",
    "ServerTime",
    "Kline",
    "Health",
]

