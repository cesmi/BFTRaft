from typing import Tuple
from Crypto.PublicKey import RSA


def gen_keys(node_ids, bits=1024) -> Tuple[dict, dict]:
    '''Generates maps from node_id -> public key and node_id -> private key
    (key pairs are randomly generated).'''

    pubkeys = {}
    privkeys = {}
    for i in node_ids:
        key = RSA.generate(bits)
        pubkey = key.publickey()
        pubkeys[i] = pubkey
        privkeys[i] = key
    return pubkeys, privkeys
