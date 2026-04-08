from __future__ import annotations

from typing import Any, Dict, Type

from sync.base import BaseSyncAdapter


class SyncFactory:
    """Creates sync adapters by registered name."""

    _adapters: Dict[str, Type[BaseSyncAdapter]] = {}

    @classmethod
    def register(cls, name: str, adapter_class: Type[BaseSyncAdapter]) -> None:
        cls._adapters[name] = adapter_class

    @classmethod
    def create(cls, name: str, **kwargs: Any) -> BaseSyncAdapter:
        if name not in cls._adapters:
            raise ValueError(f"未注册的同步适配器: {name}")
        return cls._adapters[name](**kwargs)

    @classmethod
    def list_adapters(cls) -> list:
        return list(cls._adapters.keys())
