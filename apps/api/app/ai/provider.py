from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ChatMessage:
    role: str
    content: str


class AIProvider(ABC):
    @abstractmethod
    async def complete(self, messages: Sequence[ChatMessage]) -> str:
        """Return one model completion."""

