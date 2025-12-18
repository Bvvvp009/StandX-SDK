"""Generated models from OpenAPI specification"""

from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime


# Request Models
@dataclass
class NewOrderRequest:
    symbol: str
    side: str
    order_type: str
    qty: str
    time_in_force: str
    price: Optional[str] = None
    reduce_only: Optional[bool] = None
    cl_ord_id: Optional[str] = None
    margin_mode: Optional[str] = None
    leverage: Optional[int] = None


@dataclass
class CancelOrderRequest:
    order_id: Optional[int] = None
    cl_ord_id: Optional[str] = None


@dataclass
class CancelOrdersRequest:
    order_id_list: Optional[List[int]] = None
    cl_ord_id_list: Optional[List[str]] = None


@dataclass
class ChangeLeverageRequest:
    symbol: str
    leverage: int


@dataclass
class ChangeMarginModeRequest:
    symbol: str
    margin_mode: str


@dataclass
class TransferMarginRequest:
    symbol: str
    amount_in: str
    direction: str = "add"


# Response Models
@dataclass
class OrderResponse:
    code: int
    message: str
    request_id: Optional[str] = None
    order_id: Optional[int] = None
    cl_ord_id: Optional[str] = None


@dataclass
class StandardResponse:
    code: int
    message: str
    request_id: Optional[str] = None


@dataclass
class Order:
    id: Optional[int] = None
    cl_ord_id: Optional[str] = None
    symbol: Optional[str] = None
    side: Optional[str] = None
    order_type: Optional[str] = None
    qty: Optional[str] = None
    price: Optional[str] = None
    time_in_force: Optional[str] = None
    reduce_only: Optional[bool] = None
    status: Optional[str] = None
    fill_qty: Optional[str] = None
    fill_avg_price: Optional[str] = None
    avail_locked: Optional[str] = None
    closed_block: Optional[int] = None
    created_at: Optional[str] = None
    created_block: Optional[int] = None
    updated_at: Optional[str] = None
    leverage: Optional[str] = None
    liq_id: Optional[int] = None
    margin: Optional[str] = None
    payload: Optional[dict] = None
    position_id: Optional[int] = None
    remark: Optional[str] = None
    source: Optional[str] = None
    user: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        """Create Order from API response"""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


@dataclass
class Trade:
    id: Optional[int] = None
    symbol: Optional[str] = None
    side: Optional[str] = None
    qty: Optional[str] = None
    price: Optional[str] = None
    timestamp: Optional[int] = None
    created_at: Optional[str] = None
    order_id: Optional[int] = None
    user: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Trade":
        """Create Trade from API response"""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


@dataclass
class Position:
    id: Optional[int] = None
    symbol: Optional[str] = None
    qty: Optional[str] = None
    entry_price: Optional[str] = None
    entry_value: Optional[str] = None
    leverage: Optional[int] = None
    margin_mode: Optional[str] = None
    initial_margin: Optional[str] = None
    realized_pnl: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    margin_asset: Optional[str] = None
    user: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Position":
        """Create Position from API response"""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


@dataclass
class PositionConfig:
    symbol: Optional[str] = None
    leverage: Optional[int] = None
    margin_mode: Optional[str] = None
    max_leverage: Optional[int] = None
    min_leverage: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "PositionConfig":
        """Create PositionConfig from API response"""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


@dataclass
class Balance:
    id: Optional[str] = None
    token: Optional[str] = None
    free: Optional[str] = None
    locked: Optional[str] = None
    total: Optional[str] = None
    account_type: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    inbound: Optional[str] = None
    is_enabled: Optional[bool] = None
    kind: Optional[str] = None
    last_tx: Optional[str] = None
    last_tx_updated_at: Optional[int] = None
    occupied: Optional[str] = None
    outbound: Optional[str] = None
    ref_id: Optional[int] = None
    version: Optional[int] = None
    wallet_id: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Balance":
        """Create Balance from API response"""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


@dataclass
class SymbolInfo:
    symbol: Optional[str] = None
    base: Optional[str] = None
    quote: Optional[str] = None
    status: Optional[str] = None
    min_qty: Optional[str] = None
    max_qty: Optional[str] = None
    tick_size: Optional[str] = None
    step_size: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "SymbolInfo":
        """Create SymbolInfo from API response"""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


@dataclass
class SymbolMarket:
    symbol: Optional[str] = None
    last_price: Optional[str] = None
    mark_price: Optional[str] = None
    index_price: Optional[str] = None
    volume_24h: Optional[str] = None
    turnover_24h: Optional[str] = None
    high_24h: Optional[str] = None
    low_24h: Optional[str] = None
    change_24h: Optional[str] = None
    change_percent_24h: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "SymbolMarket":
        """Create SymbolMarket from API response"""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


@dataclass
class SymbolPrice:
    symbol: Optional[str] = None
    base: Optional[str] = None
    quote: Optional[str] = None
    last_price: Optional[str] = None
    mark_price: Optional[str] = None
    index_price: Optional[str] = None
    mid_price: Optional[str] = None
    spread: Optional[List[str]] = None
    time: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "SymbolPrice":
        """Create SymbolPrice from API response"""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


@dataclass
class DepthBook:
    symbol: Optional[str] = None
    asks: Optional[List[List[str]]] = None
    bids: Optional[List[List[str]]] = None
    timestamp: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "DepthBook":
        """Create DepthBook from API response"""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


@dataclass
class RecentTrade:
    id: Optional[int] = None
    symbol: Optional[str] = None
    side: Optional[str] = None
    qty: Optional[str] = None
    price: Optional[str] = None
    timestamp: Optional[int] = None
    created_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "RecentTrade":
        """Create RecentTrade from API response"""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


@dataclass
class FundingRates:
    symbol: Optional[str] = None
    funding_rate: Optional[str] = None
    next_funding_time: Optional[int] = None
    predicted_funding_rate: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "FundingRates":
        """Create FundingRates from API response"""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


@dataclass
class ServerTime:
    server_time: Optional[int] = None
    timestamp: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "ServerTime":
        """Create ServerTime from API response"""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


@dataclass
class Kline:
    time: Optional[int] = None
    open: Optional[str] = None
    high: Optional[str] = None
    low: Optional[str] = None
    close: Optional[str] = None
    volume: Optional[str] = None
    symbol: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Kline":
        """Create Kline from API response"""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


@dataclass
class Health:
    status: Optional[str] = None
    timestamp: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Health":
        """Create Health from API response"""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})













