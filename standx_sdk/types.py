"""Type definitions and enums for StandX API"""

from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


class OrderSide(str, Enum):
    """Order side"""
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    """Order type"""
    LIMIT = "limit"
    MARKET = "market"


class OrderStatus(str, Enum):
    """Order status"""
    OPEN = "open"
    CANCELED = "canceled"
    FILLED = "filled"
    REJECTED = "rejected"
    UNTRIGGERED = "untriggered"


class TimeInForce(str, Enum):
    """Time in force"""
    GTC = "gtc"  # Good Til Canceled
    IOC = "ioc"  # Immediate Or Cancel
    ALO = "alo"  # Add Liquidity Only


class MarginMode(str, Enum):
    """Margin mode"""
    CROSS = "cross"
    ISOLATED = "isolated"


class Resolution(str, Enum):
    """Kline resolution"""
    TICK = "1T"  # 1 tick
    SEC_3 = "3S"  # 3 seconds
    MIN_1 = "1"  # 1 minute
    MIN_5 = "5"  # 5 minutes
    MIN_15 = "15"  # 15 minutes
    HOUR_1 = "60"  # 1 hour
    DAY_1 = "1D"  # 1 day
    WEEK_1 = "1W"  # 1 week
    MONTH_1 = "1M"  # 1 month


# Order, Position, and Balance are now in models.py with full field definitions

