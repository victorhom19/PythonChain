import argparse
import json
import socket
import time

from blockchain import Block
from blockchain import MessageType


class ValidBlockStub:

    def __init__(self, port):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', port))
        self.sock.setblocking(False)

    def run(self, send_to_port, delay):
        time.sleep(delay)

        block = Block(
            index=0,
            prev_hash='0XDvKDOn29vVrs7T9HCsix22Z5QDEXBaNXVcRDjnJzY9DxDKoXtQLvfhCpul20IW',
            data='fi8GXTmJ4zGlBtx1DnVY4DxxHmIILLHxza1Fl84cIjIuyJy5qdQtyrpokzHThSUz5W76adsLCJPSMzS0jVb5GeHRYlOeWerrJ7' \
                 'hZF2MhyfEu8GSxfSClDkwwMyD4h4AJ459BYWXQULteh9T0HS4QDd42wAJ2TD9K95BpmnpndMhNiQC0OSnFFRCYsWQPwUlKariN' \
                 'KpUgwMGMv8sJjrklBg2gbVvlL7U9umNP6DpKK5Vqvi4f4aBxlhtst0E29ThT',
            nonce=856847,
            hash='67df28eb159c875d4914e8fbf3ed7002b38fef13e2d17e20230f1d39e5f00000',
            author=self.port
        )

        msg = {
            'type': MessageType.ANNOUNCE_BLOCK.value,
            'block': block.__dict__
        }
        data = json.dumps(msg).encode()

        self.sock.sendto(data, ('localhost', send_to_port))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port')
    parser.add_argument('--send_to')
    parser.add_argument('--delay')
    kwargs = vars(parser.parse_args())
    stub = ValidBlockStub(int(kwargs['port']))
    stub.run(int(kwargs['send_to']), int(kwargs['delay']))
    stub.sock.close()