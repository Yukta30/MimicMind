from abc import ABC, abstractmethod
from typing import List, Dict

class LLMProvider(ABC):
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        ...

class DummyProvider(LLMProvider):
    def chat(self, messages, **kwargs) -> str:
        # Emit a deterministic unified diff for demo (no embedded triple quotes)
        return (
            "--- a/src/pager.py\n"
            "+++ b/src/pager.py\n"
            "@@ -1,6 +1,11 @@\n"
            "-class Pager:\n"
            "-    def page(self, items, size):\n"
            "-        pages = []\n"
            "-        for i in range(0, len(items)):\n"
            "-            if i % size == 0:\n"
            "-                pages.append(items[i:i+size])\n"
            "-        return pages\n"
            "+class Pager:\n"
            "+    def page(self, items, size):\n"
            "+        # Split items into pages of given size.\n"
            "+        if size <= 0:\n"
            "+            raise ValueError(\"size must be > 0\")\n"
            "+        pages = []\n"
            "+        for i in range(0, len(items), size):\n"
            "+            pages.append(items[i:i+size])\n"
            "+        return pages\n"
        )
