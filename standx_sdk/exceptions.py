"""Custom exceptions for StandX SDK"""


class StandXAPIError(Exception):
    """Base exception for all StandX API errors"""
    
    def __init__(self, message: str, code: int = None, request_id: str = None):
        self.message = message
        self.code = code
        self.request_id = request_id
        super().__init__(self.message)
    
    def __str__(self):
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message


class StandXAuthenticationError(StandXAPIError):
    """Raised when authentication fails"""
    pass


class StandXRequestError(StandXAPIError):
    """Raised when a request fails"""
    pass


class StandXWebSocketError(StandXAPIError):
    """Raised when WebSocket operations fail"""
    pass













