class Exporter:
    def run(self, items):
        for it in items:
            self._send(it)
    def _send(self, item): ...
