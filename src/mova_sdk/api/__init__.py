from typing import Any, Dict, Optional

from mova_sdk.core.engine import Engine
from mova_sdk.core.llm_client import LLMClient
from mova_sdk.core.validator import Validator
from mova_sdk.models import TaskDTO

# Lightweight SDK facade used by tests/examples.
# Keeps implementation minimal — delegates to core stubs that exist under src/mova_sdk/core.
class MovaAPI:
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.engine = Engine(config)
        self.llm = LLMClient()
        self.validator = Validator()

    def run_task(self, payload: Any) -> Any:
        return self.engine.run(payload)

    def get_status(self) -> str:
        return self.engine.status()

    def create_task(self, payload: Dict[str, Any]) -> TaskDTO:
        return TaskDTO(task_id=f"task_{hash(str(payload))}", payload=payload)

    def cache_item(self, key: str, value: Any) -> Dict[str, Any]:
        # Minimal placeholder for cache behaviour used by some tests/examples
        return {"task_id": f"task_{hash(str(key))}", "value": value}


class EngineWrapper:
    """Simple wrapper around the Engine core implementation."""
    def __init__(self, config: Optional[Any] = None) -> None:
        self.engine = Engine(config)

    def run(self, payload: Any = None) -> Any:
        return self.engine.run(payload)

    def status(self) -> str:
        return self.engine.status()


class LLMWrapper:
    """Light wrapper for LLM clients used in tests (expects client with predict/run)."""
    def __init__(self, client: Optional[Any] = None) -> None:
        self.llm = client

    def predict(self, payload: Any) -> Any:
        if self.llm is None:
            raise NotImplementedError("No LLM client configured")
        if hasattr(self.llm, "predict"):
            return self.llm.predict(payload)
        if hasattr(self.llm, "run"):
            return self.llm.run(payload)
        raise NotImplementedError("LLM client has no predict nor run")


__all__ = ["MovaAPI", "EngineWrapper", "LLMWrapper"]