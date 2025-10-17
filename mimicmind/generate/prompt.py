from typing import List
def build_prompt(ticket: str, context: str, style_tokens: List[str], mimicness: float):
    mode = "BEST_PRACTICE" if mimicness < 0.5 else "FULL_MIMIC"
    header = (
        "You are MimicMind, generating a unified diff.\n"
        f"Mode: {mode} (µ={mimicness:.2f}).\n"
        "Style tokens: " + ", ".join(style_tokens) + "\n"
        "Output ONLY a valid patch."
    )
    return [
        {"role":"system","content":header},
        {"role":"user","content":f"Ticket: {ticket}\nContext:\n{context}\n"}
    ]
