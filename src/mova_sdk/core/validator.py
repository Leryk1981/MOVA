from typing import Any, Dict, Optional


class Validator:
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}

    def validate(self, payload: Any) -> bool:
        # Minimal stub: always returns True for tests
        return True