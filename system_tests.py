import socket
import subprocess
import unittest


class BlockchainSystemTests(unittest.TestCase):

    def test_socket_closing(self):
        p = subprocess.Popen('docker-compose build'.split())
        p.wait()

        p = subprocess.Popen('docker-compose up'.split())
        p.wait()

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(('localhost', 10001))
            sock.close()

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(('localhost', 10002))
            sock.close()

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(('localhost', 10003))
            sock.close()

        except:
            self.fail()