from __future__ import annotations

from abc import ABC, abstractmethod

from repopilot.models import AgentAction, Message, ProviderMetadata


class AgentProvider(ABC):
    name = "unknown"
    adapter = "native"

    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(name=self.name, adapter=self.adapter)

    @abstractmethod
    def next_action(self, messages: list[Message]) -> AgentAction:
        raise NotImplementedError
