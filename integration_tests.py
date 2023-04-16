import asyncio
import concurrent
import json
import subprocess
import time
import unittest
import socket

from pebble import ProcessPool

from blockchain import Node, run_node
from spy import AnnounceBlockSpy


class BlockchainIntegrationTest(unittest.TestCase):

    def setUp(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    def test_block_generation_and_announcement(self):
        spy = AnnounceBlockSpy(port=10003, total=3)

        p = subprocess.Popen('python ./blockchain.py --port 10001 --genesis 1 --log 0'.split())

        with ProcessPool() as pool:
            spy_future = pool.schedule(AnnounceBlockSpy.listen, args=[spy], timeout=60)

        try:
            spy_future.result()
            p.kill()
            spy.close()
            time.sleep(10)
        except concurrent.futures._base.TimeoutError:
            p.kill()
            spy.close()
            time.sleep(10)
            self.fail()

    def test_block_adoption(self):
        node = Node(port=10001, genesis=0, timeout=60)
        node.total_blocks = 3
        p = subprocess.Popen('python ./stub.py --port 10003 --send_to 10001 --delay 10'.split())

        blockchain = asyncio.run(run_node(node))
        node.sock.close()
        p.kill()
        time.sleep(10)
        assert len(blockchain) == 3
        assert blockchain[0].hash == '67df28eb159c875d4914e8fbf3ed7002b38fef13e2d17e20230f1d39e5f00000'

    def test_block_rejection(self):
        node = Node(port=10001, genesis=1, timeout=60)
        node.total_blocks = 3

        p = subprocess.Popen('python ./stub.py --port 10003 --send_to 10001 --delay 20'.split())

        blockchain = asyncio.run(run_node(node))
        node.sock.close()
        p.kill()
        time.sleep(10)
        assert len(blockchain) > 0
        for block in blockchain:
            assert (block.hash != '67df28eb159c875d4914e8fbf3ed7002b38fef13e2d17e20230f1d39e5f00000')

    def test_node_synchronization(self):
        node = Node(port=10001, genesis=1, timeout=60)
        node.total_blocks = 8

        p = subprocess.Popen('python ./spy_and_stub.py --port 10003 --send_to 10001 --delay 3'.split())

        blockchain = asyncio.run(run_node(node))
        node.sock.close()
        p.kill()
        time.sleep(10)
        assert (blockchain[0].hash == 'cdf0f12a769ff0c983be57adec2436b2e3e531d27dc5627f32d83dc63b000000')
        assert (blockchain[1].hash == '47fb2cebbf2df7106efc9a9c32f7a94977f5035dc2eebeb13acccde5e4a00000')
        assert (blockchain[2].hash == '91079792073937c946053a3613629376bedf33a8759f8dbb470a13e132a00000')
        assert (blockchain[3].hash == 'e06abfdaa90c5f273dbc1e9bb3951efad18c4c872dd6e4f146d6cd1dae900000')
        assert (blockchain[4].hash == 'feae5388c7c38d88696b350237c68a6dcc9b110cedaef6eb0c8dc7605e100000')

    def test_full_node_interaction(self):
        node1 = Node(port=10001, genesis=1, timeout=100)
        node1.total_blocks = 100
        node2 = Node(port=10002, genesis=0, timeout=100)
        node2.total_blocks = 100
        node3 = Node(port=10003, genesis=0, timeout=100)
        node3.total_blocks = 100
        loop = asyncio.get_event_loop()
        tasks = asyncio.gather(run_node(node1), run_node(node2), run_node(node2))
        node1.sock.close()
        node2.sock.close()
        node3.sock.close()
        time.sleep(10)
        blockchain1, blockchain2, blockchain3 = loop.run_until_complete(tasks)
        for block1, block2, block3 in zip(blockchain1[:-2], blockchain2[:-2], blockchain3[:-2]):
            assert block1.hash == block2.hash == block3.hash

if __name__ == '__main__':
    unittest.main()