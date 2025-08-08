"""
Core engine for MOVA SDK - orchestrates tasks and integrates components.
This MVP implementation provides state management and basic caching.
"""

from typing import Any, Dict, Optional


class Engine:
    """
    Engine with explicit state management and caching capabilities.
    
    Attributes:
        _state (str): Current engine state ('idle' or 'running').
        _cache (Dict[str, Any]): Key-value storage for caching.
        _config (Dict[str, Any]): Engine configuration.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize engine with optional configuration.
        
        Args:
            config: Optional configuration dictionary.
        """
        self._state = "idle"
        self._cache: Dict[str, Any] = {}
        self._config = config or {}

    def run(self, payload: Any = None) -> Any:
        """
        Execute engine operation with payload processing and caching.
        
        Args:
            payload: Input data (if dict with 'cache_key' and 'value', will be cached).
            
        Returns:
            Processed payload or cached value.
        """
        self._state = "running"
        
        try:
            if isinstance(payload, dict) and 'cache_key' in payload and 'value' in payload:
                self._cache[payload['cache_key']] = payload['value']
                result = payload['value']
            else:
                result = payload
            return result
        finally:
            self._state = "idle"

    def status(self) -> str:
        """Return current engine state."""
        return self._state

    def put_cache(self, key: str, value: Any) -> None:
        """Store value in cache."""
        self._cache[key] = value

    def get_cache(self, key: str, default: Any = None) -> Any:
        """
        Retrieve cached value by key.
        
        Args:
            key: Cache key to lookup.
            default: Default value if key not found.
            
        Returns:
            Cached value or default if not found.
        """
        return self._cache.get(key, default)

    def clear_cache(self) -> None:
        """Clear all cached values."""
        self._cache.clear()