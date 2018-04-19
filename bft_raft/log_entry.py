import pickle
from Crypto.Hash import SHA256
from .config import BaseConfig
from .messages import ClientRequest, SignedMessage


class LogEntry(object):
    def __init__(self, term: int, prev_incremental_hash: bytes,
                 client_request: SignedMessage[ClientRequest]) -> None:
        self.term = term
        self.prev_incremental_hash = prev_incremental_hash
        self.signed = client_request

    @property
    def operation(self):
        return self.signed.message.operation

    @property
    def client_id(self):
        return self.signed.message.client_id

    def incremental_hash(self) -> bytes:
        return SHA256.new(pickle.dumps(self)).digest()

    def verify(self, config: BaseConfig) -> bool:
        return True  # TODO
