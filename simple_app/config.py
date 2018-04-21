import os
import sys
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

from Crypto.PublicKey import RSA


client_addrs = {}
for i in range(50):
    client_addrs[i] = ('127.0.0.1', 8000 + i)

server_addrs = {
    0: ('127.0.0.1', 9000),
    1: ('127.0.0.1', 9001),
    2: ('127.0.0.1', 9002),
    3: ('127.0.0.1', 9003)
}


def read_pubkeys(prefix, num_keys):
    public = {}
    for i in range(num_keys):
        public_fname = '%s%d_public.pem' % (prefix, i)
        public_f = open(public_fname, 'r')
        public[i] = RSA.importKey(public_f.read())
    return public


def read_privkey(prefix, num):
    return RSA.importKey(
        open('%s%d_private.pem' % (prefix, num), 'r').read())


client_pubkeys = read_pubkeys('client', 4)
server_pubkeys = read_pubkeys('server', 4)
