import hashlib
import random

import unittest
from blockchain import Node, Block


class BlockchainTest(unittest.TestCase):

    # Test first block generation with pre-calculated hash and set random seed
    def test_block_generation_1(self):
        node = Node(port=10001, genesis=1)
        random.seed(12345)
        block = node.mine_block()
        assert (block is not None)
        assert (len(block.hash) == 64)
        assert (block.hash == 'ca73d479c80506406841394c9289212410eec84f8b27e4f296bf0a1657c00000')

    # Test pure first block generation
    def test_block_generation_2(self):
        node = Node(port=10001, genesis=1)
        block = node.mine_block()
        assert (block is not None)
        assert (validate_custom_block_hash(block))
        assert (len(block.hash) == 64)

    # Test first block generation with genesis set to 0
    def test_block_generation_3(self):
        node = Node(port=10001, genesis=0)
        block = node.mine_block()
        assert (block is None)

    # Test block generation with pre-generated first block
    def test_block_generation_4(self):
        node = Node(port=10001, genesis=0)
        first_block = Block(
            index=0,
            prev_hash='F4dGBuWdpjnzHdAzH8g81yJWRMg6JJd2NyIu4ElOwM80BLUoB0lqzFFa3XQC5k5w',
            data='xyKcTcggeHqJNYWSndwS9ClPziOnt2GMC5kVDWM4CBif16hj3GSD5vMzGDhNshdJfef0Z6dmoH7pfNbj8MxoGW6F6InTkteM3Dc'
                 'IS1NLi84n2zNxNIKYDtZj5OwWZNG34RbtEa264Mv2dY4AOR8Xlf1lUYNxvJPOsUuFT70aSsRHfFK82AJoElT2VkSdoTpOjt1S71'
                 'q18Z17m9hJUsVLv8pgddAagRQCLO0dyAdFMStwmdtm5D87nkhLLE7Jc8Jd',
            hash='',
            nonce=0,
            author=10001
        )
        node.blockchain.append(first_block)
        block = node.mine_block()
        assert (block is not None)
        assert (block.index == 1)
        assert (block.prev_hash == first_block.hash)

    # Test chain generation and hash integrity
    def test_chain_generation_1(self):
        node = Node(port=10001, genesis=1, timeout=60)
        node.total_blocks = 5
        node.work()
        assert (len(node.blockchain) == 5)
        for i, _ in enumerate(node.blockchain[:-1]):
            assert (node.blockchain[i].hash == node.blockchain[i + 1].prev_hash)


    # Test chain generation with genesis set to 0
    def test_chain_generation_2(self):
        node = Node(port=10001, genesis=0, timeout=30)
        node.work()
        assert len(node.blockchain) == 0


def validate_custom_block_hash(block):
    true_hash = hashlib.sha256(
        (str(block.index) + block.prev_hash + block.data + str(block.nonce)).encode()).hexdigest()
    return true_hash == block.hash


if __name__ == '__main__':
    unittest.main()