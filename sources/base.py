from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseSource(ABC):
    """Abstract base class for data sources."""

    @abstractmethod
    def load(self, path: str) -> List[Dict[str, Any]]:
        """Load raw data from file. Returns list of raw items."""
        ...

    @abstractmethod
    def extract_user_text(self, item: Dict[str, Any]) -> str | None:
        """Extract user text from a single item. Returns None if not found."""
        ...

    def process(self, path: str) -> List[str]:
        """Load and extract user texts. Returns list of valid strings."""
        data = self.load(path)
        texts = []
        for item in data:
            text = self.extract_user_text(item)
            if text:
                texts.append(text)
        return texts