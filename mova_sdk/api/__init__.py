from typing import Any, Optional


# Simple wrappers around existing core Engine
class EngineWrapper:
    def __init__(self, config: Optional[Any] = None):
        from mova_sdk.core.engine import Engine as CoreEngine
        self.engine = CoreEngine(config)

    def run(self, payload: Any = None) -> Any:
        return self.engine.run(payload)

    def status(self) -> str:
        return self.engine.status()


class LLMWrapper:
    def __init__(self, client: Optional[Any] = None):
        self.llm = client if client is not None else None

    def predict(self, payload: Any) -> Any:
        if hasattr(self.llm, "predict"):
            return self.llm.predict(payload)
        if hasattr(self.llm, "run"):
            return self.llm.run(payload)
        raise NotImplementedError("LLM client has no predict nor run")


__all__ = ["EngineWrapper", "LLMWrapper"]