from abc import ABC, abstractmethod
from typing import List, Dict

class LLMProvider(ABC):
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str: ...

class DummyProvider(LLMProvider):
    def chat(self, messages, **kwargs) -> str:
        # Emit a deterministic unified diff for demo.
        return """--- a/src/pager.py
+++ b/src/pager.py
@@ -1,6 +1,12 @@
-class Pager:
-    def page(self, items, size):
-        pages = []
-        for i in range(0, len(items)):
-            if i % size == 0:
-                pages.append(items[i:i+size])
-        return pages
+class Pager:
+    def page(self, items, size):
+        """Split items into pages of given size.
+        Mimics a particular style: explicit guard, simple loop.
+        """
+        if size <= 0:
+            raise ValueError("size must be > 0")
+        pages = []
+        for i in range(0, len(items), size):
+            pages.append(items[i:i+size])
+        return pages
"""
