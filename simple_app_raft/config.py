import os
import sys
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

client_addrs = {}
for i in range(50):
    client_addrs[i] = ('127.0.0.1', 8000 + i)

server_addrs = {
    0: ('127.0.0.1', 9000),
    1: ('127.0.0.1', 9001),
    2: ('127.0.0.1', 9002)
}
