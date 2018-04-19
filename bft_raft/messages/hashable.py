from math import ceil
from Crypto.Hash import SHA256


class Hashable(object):
    def hash(self) -> bytes:
        '''Returns the SHA256 hash of the object.'''
        h = SHA256.new()
        self.update_hash(h)
        return h.digest()

    def update_hash(self, h) -> None:
        '''Updates the hash with each field of the object.'''
        raise NotImplementedError

    def int_to_bytes(self, x: int) -> bytes:
        length = ceil(x.bit_length() / 8)
        return x.to_bytes(length, byteorder='big')
