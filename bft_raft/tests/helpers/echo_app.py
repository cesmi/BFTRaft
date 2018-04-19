from ...application import Application


class EchoApp(Application):
    def handle_request(self, operation: bytes, client_id: int) -> bytes:
        return operation
