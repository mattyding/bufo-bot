from abc import ABC, abstractmethod
from typing import Optional, Any


class AbstractHandler(ABC):
    """Abstract base class for message handlers"""

    def __init__(self, cfg: Any):
        pass

    @abstractmethod
    async def handle(self, *args, **kwargs) -> Optional[str]:
        raise NotImplementedError
