class Patcher:
    def __init__(self, provider):
        self.provider = provider
    def propose_patch(self, ticket, context, **kwargs):
        messages = [
            {"role": "system", "content": "You propose code patches as unified diffs."},
            {"role": "user", "content": f"Ticket: {ticket.get('key')} - {ticket.get('summary')}\nContext:\n{context}"}
        ]
        return self.provider.chat(messages, **kwargs)
