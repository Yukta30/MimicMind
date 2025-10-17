import re
from typing import List
class BugRule:
    def __init__(self, name: str, pattern: str, hint: str):
        self.name, self.pattern, self.hint = name, re.compile(pattern), hint
DEFAULT_BUGS: List[BugRule] = [
    BugRule("off_by_one","range\(.*len\(.*\)\)","Check inclusive/exclusive bounds"),
    BugRule("missing_await", r"async\s+def[\s\S]*[^_]\b\w+\(.*\)\n", "Await async calls"),
]
