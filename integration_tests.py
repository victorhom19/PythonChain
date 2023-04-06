import asyncio
import concurrent
import subprocess
import unittest

from pebble import ProcessPool

from blockchain import Node, run_node
from spy import AnnounceBlockSpy


class BlockchainIntegrationTest(unittest.TestCase):

    def setUp(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    def test_block_generation_and_announcement(self):
        spy = AnnounceBlockSpy(port=10003, total=5)

        p = subprocess.Popen('python blockchain.py --port 10001 --genesis 1'.split())

        with ProcessPool() as pool:
            spy_future = pool.schedule(AnnounceBlockSpy.listen, args=[spy], timeout=30)

        try:
            p.kill()
            spy.close()
            spy_future.result()
        except concurrent.futures._base.TimeoutError:
            self.fail()

    def test_block_adoption(self):
        node = Node(port=10001, genesis=0, timeout=40)
        node.total_blocks = 5
        subprocess.Popen('python stub.py --port 10003 --send_to 10001 --delay 10')

        blockchain = asyncio.run(run_node(node))
        assert len(blockchain) == 5
        assert blockchain[0].hash == '67df28eb159c875d4914e8fbf3ed7002b38fef13e2d17e20230f1d39e5f00000'

    def test_block_rejection(self):
        node = Node(port=10001, genesis=1, timeout=40)
        node.total_blocks = 5

        subprocess.Popen('python stub.py --port 10003 --send_to 10001 --delay 5')

        blockchain = asyncio.run(run_node(node))

        assert len(blockchain) > 0
        for block in blockchain:
            assert (block.hash != '67df28eb159c875d4914e8fbf3ed7002b38fef13e2d17e20230f1d39e5f00000')
