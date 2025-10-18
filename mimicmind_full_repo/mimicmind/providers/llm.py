from abc import ABC, abstractmethod
from typing import List, Dict

class LLMProvider(ABC):
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        ...

class DummyProvider(LLMProvider):
    def chat(self, messages, **kwargs) -> str:
        mu = float(kwargs.get("mu", 0.4))
        key = str(kwargs.get("key", "")).upper()

        if key in ("DEMO-2", "WB-2"):
            if mu >= 0.75:
                return (
                    "--- a/src/exporter.py\n"
                    "+++ b/src/exporter.py\n"
                    "@@ -1,4 +1,9 @@\n"
                    " class Exporter:\n"
                    "     def run(self, items):\n"
                    "+        print(\"export:start\", len(items))\n"
                    "         for it in items:\n"
                    "             self._send(it)\n"
                    "+        print(\"export:done\")\n"
                )
            else:
                return (
                    "--- a/src/exporter.py\n"
                    "+++ b/src/exporter.py\n"
                    "@@ -1,4 +1,7 @@\n"
                    " class Exporter:\n"
                    "     def run(self, items):\n"
                    "+        # add simple progress logging\n"
                    "+        print(len(items))\n"
                    "         for it in items:\n"
                    "             self._send(it)\n"
                )

        if mu >= 0.75:
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
