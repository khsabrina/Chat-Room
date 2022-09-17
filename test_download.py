import unittest
from threading import Thread
import io
import unittest.mock
# from .solution import fizzbuzz
import time

from server import Server
from client import Client
import filecmp
import pytest


class Test_download(unittest.TestCase):

    def test_download_file(self):
        client = Client()
        server = Server()
        Thread(target=server.start).start()
        client.start("sabrina")
        time.sleep(1)
        client.download_file("test.txt", "test.txt")
        time.sleep(4)
        self.assertEqual("<download><test.txt>", server.last_message_test)
        #time.sleep(1)
        client.proceed_download()
        time.sleep(15)
        self.assertTrue(filecmp.cmp("test.txt", "./serversFiles/test.txt"))
        client.download_file("test2.txt", "test.txt")
        time.sleep(2)
        self.assertEqual("The file doesn't exist", client.last_message_test)
        server.server_disconnect()



if __name__ == '__main__':
    Test_download.test_download_file()
