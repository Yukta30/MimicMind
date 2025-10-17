from .prompt import build_prompt
from ..providers.llm import LLMProvider, DummyProvider

class Patcher:
    def __init__(self, llm: LLMProvider | None = None, style_tokens=None, mimicness: float = 0.4):
        self.llm = llm or DummyProvider()
        self.style_tokens = style_tokens or ["avg_func_len=14.2","camel_ratio=0.12","docstring_ratio=0.30","log_usage=0.18"]
        self.mimicness = mimicness
    def propose_patch(self, ticket_text: str, code_context: str) -> str:
        messages = build_prompt(ticket_text, code_context, self.style_tokens, self.mimicness)
        return self.llm.chat(messages)
