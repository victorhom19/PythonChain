import hashlib
import random
import string
import time


class Block:

    def __init__(self, index, prev_hash, hash, data, nonce):
        self.index = index
        self.prev_hash = prev_hash
        self.hash = hash
        self.data = data
        self.nonce = nonce


class Node:

    def __init__(self, genesis, total_blocks=10, timeout=120):
        self.genesis = genesis
        self.total_blocks = total_blocks
        self.timeout = timeout

        self.blockchain = []
        self.init_time = time.perf_counter()


    def work(self):
        while True:
            block = self.mine_block()

            if block is not None:
                if self.validate_block(block):
                    self.blockchain.append(block)
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
            nonce += random.randint(0, 10_000_000)
            hash = hashlib.sha256((str(index) + prev_hash + data + str(nonce)).encode()).hexdigest()
            if int(hash[-5:], 16) == 0:
                block = Block(
                    index=index,
                    prev_hash=prev_hash,
                    data=data,
                    hash=str(hash),
                    nonce=nonce
                )
                return block