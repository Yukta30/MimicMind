from abc import ABC, abstractmethod
from typing import List, Dict

class LLMProvider(ABC):
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        ...

class DummyProvider(LLMProvider):
    def chat(self, messages, **kwargs) -> str:
        mu = float(kwargs.get("mu", 0.4))
        key = (kwargs.get("key") or "").upper()

        # Two clearly different patches so the slider "pops"
        if mu >= 0.75:
            # Best-practice tilt: docstring + validation + proper stepping
            return (
                "--- a/src/pager.py\n"
                "+++ b/src/pager.py\n"
                "@@ -1,6 +1,13 @@\n"
                "-class Pager:\n"
                "-    def page(self, items, size):\n"
                "-        pages = []\n"
                "-        for i in range(0, len(items)):\n"
                "-            if i % size == 0:\n"
                "-                pages.append(items[i:i+size])\n"
                "-        return pages\n"
                "+class Pager:\n"
                "+    def page(self, items, size):\n"
                "+        \"\"\"Split items into pages of given size.\"\"\"\n"
                "+        if size <= 0:\n"
                "+            raise ValueError(\"size must be > 0\")\n"
                "+        pages = []\n"
                "+        for i in range(0, len(items), size):\n"
                "+            pages.append(items[i:i+size])\n"
                "+        return pages\n"
            )
        else:
            # Quirk-preserving: minimal change, fixes boundary with less opinion
            return (
                "--- a/src/pager.py\n"
                "+++ b/src/pager.py\n"
                "@@ -1,6 +1,9 @@\n"
                " class Pager:\n"
                "-    def page(self, items, size):\n"
                "-        pages = []\n"
                "-        for i in range(0, len(items)):\n"
                "-            if i % size == 0:\n"
                "-                pages.append(items[i:i+size])\n"
                "-        return pages\n"
                "+    def page(self, items, size):\n"
                "+        # keep shape; fix boundary by stepping size\n"
                "+        pages = []\n"
                "+        for i in range(0, len(items), max(1, size)):\n"
                "+            pages.append(items[i:i+size])\n"
                "+        return pages\n"
            )
