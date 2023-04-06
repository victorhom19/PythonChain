import json
import socket

from blockchain import MessageType


class AnnounceBlockSpy:
    def __init__(self, port, total):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', port))
        self.sock.setblocking(False)
        self.total = total

    def listen(self):
        block_count = 0
        while True:
            try:
                data, addr = self.sock.recvfrom(512)
                msg = json.loads(data.decode())
                assert (msg.get('type') == MessageType.ANNOUNCE_BLOCK.value)
                block = msg.get('block')
                assert (block is not None)
                block_count += 1
                if block_count == self.total:
                    return True
            except:
                pass

    def close(self):
        self.sock.close()