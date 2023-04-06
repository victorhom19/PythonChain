import argparse
import asyncio
import concurrent
import json
import socket
import time

from blockchain import Block, MessageType


class SpyAndStub:

    def __init__(self, port):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', port))
        self.sock.setblocking(False)
        self.prepared_blockchain = [
            Block(
                index=0,
                prev_hash='tVZcYgDm5k4S4llPOriPE03O9kMMyGsR40ENrOIxh0LVqJvzRsXHT1fx1xlbu5V1',
                data='p6h42l2tMcpvKFHuuV16MBuOIzDItFzHENP620tQG2xiqTmkd9BVZodXLaeo7hKWJ92Hs'
                     'jtI1wCd82BBcceh5LJCsnLhLuMB5rBgE95WZ97z0OW1iZ5CKiIT1le8pDz9YEXyv38qzn'
                     '1ov0dOtHkEFHCGxxkQWaMSMldwhp5AfwR1UIY3mrDANemOq2VQXwdkejMKkIc0J1P7rve'
                     'iS0Umv6ZIhUhHGUdA2kniVU01JOoTjmCGGRUNX4EERQVa8M9u',
                nonce=6882102118500,
                hash='cdf0f12a769ff0c983be57adec2436b2e3e531d27dc5627f32d83dc63b000000',
                author=self.port,
            ),
            Block(
                index=1,
                prev_hash='cdf0f12a769ff0c983be57adec2436b2e3e531d27dc5627f32d83dc63b000000',
                data='JnzeSNiRzXIZnVWgM4lVSsi1aSQQicssPvF8iWMzNcM3KvQqhRgLmPBDmYzblIZySntmQ'
                     'y7EpkgVxwbD8xvTqfUN5mLON8C1YYuRXkECx3H8HHBQdK3VmSYsOIy3WmvWSfKTmAtRkr'
                     'mVvxyTHtM4AHxRxUIec0XhbqSKBdJK1X3E46nwnDovcyxjXUTGVVkl0STgsKkSg5P8Mxk'
                     'L4pZEimz7kIpr7COAN3RTrr1a9XAqUDOJEZq2SdYd0C5jPD8d',
                nonce=1596685715300,
                hash='47fb2cebbf2df7106efc9a9c32f7a94977f5035dc2eebeb13acccde5e4a00000',
                author=self.port,
            ),
            Block(
                index=2,
                prev_hash='47fb2cebbf2df7106efc9a9c32f7a94977f5035dc2eebeb13acccde5e4a00000',
                data='ATD57x9T0V1ZLD3AdKaOJumETyUAw68BQy8EmP8R2OMQNCSCE9Ka34SE1apSeTdhTZXv0'
                     'yb6iz2wDP5jStbn3gjx79HWafjch8SSTv4APxeUKMP6ICcMz3SdP4gNUEzgz4GXQRAMZW'
                     'hIg3MkZmujtwTWaMiXVtmkhNwSUDaMMGXZwWcMgQlurluNM7iRO3tmQa2TIHbxM8uZvKL'
                     'INp3b5VJn3ioL4jckdtgNjJ3oBpbyBUgdV5kFS9HZpx6VBBqH',
                nonce=1171204648173,
                hash='91079792073937c946053a3613629376bedf33a8759f8dbb470a13e132a00000',
                author=self.port,
            ),
            Block(
                index=3,
                prev_hash='91079792073937c946053a3613629376bedf33a8759f8dbb470a13e132a00000',
                data='Qp6I2548lHISTsaozjRKg3br1pQGtUFWN8G2UEWFRS3EdyetxNmQPijOT0t3xGxRVd7Kp'
                     'y2eRfiMjPJnb2Q1mQ7PPp4ZmRHFQgXdfauhE58akKOlukYrixic56JA5N3zyCwocvHhaw'
                     '2CXMCcpwD9KW0xFOu3pUVnghNrF3GRqhM618U4ezsif1hfpqD11TfaKaCHvo8iwhMTYQb'
                     'kVeclBk5iKTKV3RXFfWhY2UtXBEhGwtFyMirjn9ZkYR0DRBNE',
                nonce=2481266592333,
                hash='e06abfdaa90c5f273dbc1e9bb3951efad18c4c872dd6e4f146d6cd1dae900000',
                author=self.port,
            ),
            Block(
                index=4,
                prev_hash='e06abfdaa90c5f273dbc1e9bb3951efad18c4c872dd6e4f146d6cd1dae900000',
                data='IXsiocyZhUvEjj11T3POiVz2IkwTIudL7vBWnmeKTFNMO3Y2cdmgq1xF361wBrS2jg3FQ'
                     'Q7tYFBou04vmKdcLsL6aODMuXNEPlsCubRHELHl542GoIAPMzEbJZAikczN1oU7gBinkY'
                     'G3XE8Cd2te0v6l3DmqnUkVlmsVMU13wNvIYH6v37rnPGvIQEc0fDzcGF32wt9XRJ68eqQ'
                     'XVt3G3b1W7ElOitI0fUytXLqSJ297FLOuB8yDILyDm8u2oKOx',
                nonce=13809278226562,
                hash='feae5388c7c38d88696b350237c68a6dcc9b110cedaef6eb0c8dc7605e100000',
                author=self.port,
            )
        ]

    def send(self, send_to_port, delay):
        time.sleep(delay)

        msg = {
            'type': MessageType.ANNOUNCE_BLOCK.value,
            'block': self.prepared_blockchain[-1].__dict__
        }
        data = json.dumps(msg).encode()
        self.sock.sendto(data, ('localhost', send_to_port))

    def listen(self, send_to_port):
        while True:
            try:
                data, addr = self.sock.recvfrom(512)
                msg = json.loads(data.decode())
                assert (msg.get('type') == MessageType.CHAIN_REQUEST.value)
                for block in self.prepared_blockchain[:-1]:
                    time.sleep(0.1)

                    msg = {
                        'type': MessageType.SEND_CHAIN.value,
                        'block': block.__dict__
                    }
                    data = json.dumps(msg).encode()
                    self.sock.sendto(data, ('localhost', send_to_port))

                time.sleep(0.1)

                msg = {
                    'type': MessageType.SEND_CHAIN.value,
                    'block': self.prepared_blockchain[-1].__dict__,
                    'last': 1
                }
                data = json.dumps(msg).encode()
                self.sock.sendto(data, ('localhost', send_to_port))
            except:
                pass

async def run(spy_and_stub):
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
    loop = asyncio.get_event_loop()
    await asyncio.wait(
        fs={
            loop.run_in_executor(executor, spy_and_stub.listen),
            loop.run_in_executor(executor, spy_and_stub.send)
        }
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port')
    parser.add_argument('--send_to')
    parser.add_argument('--delay')
    kwargs = vars(parser.parse_args())
    spy_and_stub = SpyAndStub(int(kwargs['port']))
    spy_and_stub.send(int(kwargs['send_to']), int(kwargs['delay']))
    spy_and_stub.listen(int(kwargs['send_to']))
    spy_and_stub.sock.close()