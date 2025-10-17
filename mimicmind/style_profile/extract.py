import ast, re
from pathlib import Path
from statistics import mean

class StyleProfile:
    def __init__(self):
        self.avg_func_len = 0.0
        self.camel_ratio = 0.0
        self.docstring_ratio = 0.0
        self.log_usage = 0.0
    def to_tokens(self):
        return [
            f"avg_func_len={self.avg_func_len:.1f}",
            f"camel_ratio={self.camel_ratio:.2f}",
            f"docstring_ratio={self.docstring_ratio:.2f}",
            f"log_usage={self.log_usage:.2f}",
        ]

snake = re.compile(r"^[a-z]+(_[a-z0-9]+)*$")
camel = re.compile(r"^[A-Z][a-zA-Z0-9]+$")

class PyAnalyzer:
    def analyze(self, root: str) -> StyleProfile:
        fn_lengths, camel_names, snake_names, doc_funcs, logged, funcs = [],0,0,0,0,0
        for p in Path(root).rglob("*.py"):
            try: tree = ast.parse(p.read_text(encoding="utf-8"))
            except Exception: continue
            for n in ast.walk(tree):
                if isinstance(n, ast.FunctionDef):
                    funcs += 1
                    start = getattr(n, 'lineno', 0)
                    end = max([getattr(m,'lineno',start) for m in ast.walk(n)], default=start)
                    fn_lengths.append(max(1, end - start))
                    if ast.get_docstring(n): doc_funcs += 1
                    if snake.match(n.name): snake_names += 1
                    if camel.match(n.name): camel_names += 1
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
                    if getattr(n.func.value,'id',None) in {"log","logger","logging"}:
                        logged += 1
        sp = StyleProfile()
        sp.avg_func_len = mean(fn_lengths) if fn_lengths else 0
        total_names = camel_names + snake_names or 1
        sp.camel_ratio = camel_names/total_names
        sp.docstring_ratio = (doc_funcs/(funcs or 1))
        sp.log_usage = logged / (funcs or 1)
        return sp
