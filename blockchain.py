import argparse
import asyncio
import concurrent
import hashlib
import json
import random
import string
import time
from enum import Enum
import socket


class Block:

    def __init__(self, index, prev_hash, hash, data, nonce, author):
        self.index = index
        self.prev_hash = prev_hash
        self.hash = hash
        self.data = data
        self.nonce = nonce
        self.author = author


class MessageType(Enum):
    ANNOUNCE_BLOCK = 0
    CHAIN_REQUEST = 1
    SEND_CHAIN = 2

class Node:

    def __init__(self, port, genesis, total_blocks=10, timeout=120, log=False):
        self.port = port
        self.genesis = genesis
        self.total_blocks = total_blocks
        self.timeout = timeout
        self.log = log

        self.blockchain = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', self.port))
        self.sock.setblocking(False)
        self.lock = False
        self.interrupt = False

        self.init_time = time.perf_counter()

    def listen(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(512)
                msg = json.loads(data.decode())
                if msg.get('type') == MessageType.ANNOUNCE_BLOCK.value and not self.lock:
                    block = Block(**msg.get('block'))
                    if self.validate_block(block):
                        self.interrupt = True
                        self.blockchain.append(block)
                    elif block.index > len(self.blockchain):
                        self.lock = True
                        _, port = addr
                        found = False
                        for i, block in enumerate(self.blockchain[::-1]):
                            if block.author == port:
                                found = True
                                self.blockchain = self.blockchain[:-i]
                                break
                        if not found:
                            self.blockchain = []
                        if len(self.blockchain) == 0:
                            block = None
                        else:
                            block = self.blockchain[-1].__dict__
                        msg = {
                            'type': MessageType.CHAIN_REQUEST.value,
                            'block': block
                        }
                        data = json.dumps(msg).encode()
                        self.sock.sendto(data, ('localhost', port))

                elif msg.get('type') == MessageType.CHAIN_REQUEST.value and not self.lock:
                    index_from = 0
                    if msg.get('block') is not None:
                        block = Block(**msg.get('block'))
                        for i, bl in enumerate(self.blockchain):
                            if bl.hash == block.hash:
                                index_from = i
                                break
                    i = index_from
                    while i < len(self.blockchain):
                        msg = {
                            'type': MessageType.SEND_CHAIN.value,
                            'block': self.blockchain[i].__dict__,
                            'last': 1 if i == len(self.blockchain) - 1 else 0
                        }
                        data = json.dumps(msg).encode()
                        _, port = addr
                        self.sock.sendto(data, ('localhost', port))
                        i += 1

                elif msg.get('type') == MessageType.SEND_CHAIN.value:
                    block = Block(**msg.get('block'))
                    if self.validate_block(block):
                        self.blockchain.append(block)
                        last = msg.get('last')
                        if last:
                            self.lock = False
            except:
                pass

            if len(self.blockchain) >= self.total_blocks or time.perf_counter() - self.init_time >= self.timeout:
                break

    def work(self):
        while True:
            block = self.mine_block()
            if block is not None:
                if self.validate_block(block):
                    self.blockchain.append(block)
                    msg = {
                        'type': MessageType.ANNOUNCE_BLOCK.value,
                        'block': block.__dict__
                    }
                    data = json.dumps(msg).encode()
                    for port in (10001, 10002, 10003):
                        if self.port != port:
                            self.sock.sendto(data, ('localhost', port))

            if len(self.blockchain) >= self.total_blocks or time.perf_counter() - self.init_time >= self.timeout:
                return self.blockchain

    def validate_block(self, block):
        return block.index == len(self.blockchain) and \
               (len(self.blockchain) == 0 or self.blockchain[-1].hash == block.prev_hash)

    def mine_block(self):
        index = len(self.blockchain)
        if index > 0:
            prev_hash = self.blockchain[-1].hash
        elif self.genesis:
            prev_hash = ''.join(random.choices(string.ascii_letters+string.digits, k=64))
        else:
            return None
        data = ''.join(random.choices(string.ascii_letters+string.digits, k=256))
        nonce = 0
        while True:
            if self.lock:
                return None
            if self.interrupt:
                self.interrupt = False
                return None
            nonce += random.randint(0, 10_000_000)
            hash = hashlib.sha256((str(index) + prev_hash + data + str(nonce)).encode()).hexdigest()
            if int(hash[-5:], 16) == 0:
                block = Block(
                    index=index,
                    prev_hash=prev_hash,
                    data=data,
                    hash=str(hash),
                    nonce=nonce,
                    author=self.port
                )
                return block

async def run_node(node):
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
    loop = asyncio.get_event_loop()
    await asyncio.wait(
        fs={
            loop.run_in_executor(executor, node.listen),
            loop.run_in_executor(executor, node.work)
        }
    )
    node.sock.close()
    if node.log:
        print(json.dumps(node.blockchain[-1].__dict__, indent=4))
    return node.blockchain


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port')
    parser.add_argument('--genesis')
    parser.add_argument('--log')
    kwargs = vars(parser.parse_args())
    node = Node(int(kwargs['port']), int(kwargs['genesis']), log=bool(int(kwargs['log'])))
    asyncio.run(run_node(node))
    node.sock.close()