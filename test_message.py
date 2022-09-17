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


class Test_message(unittest.TestCase):

    def test_message_client(self):
        client = Client()
        server = Server()
        Thread(target=server.start).start()
        client.start("Sabrina")
        time.sleep(2)
        self.assertEqual("Sabrina is connected", client.last_message_test)
        client.send_msg("Hey")
        time.sleep(0.2)
        self.assertEqual("<set_msg_all><Hey>", server.last_message_test)
        self.assertEqual("Sabrina: Hey", client.last_message_test)
        client.send_msg("Hey", "Sabrina")
        time.sleep(0.2)
        self.assertEqual("<set_msg><Sabrina><Hey>", server.last_message_test)
        self.assertEqual("Sabrina: Hey", client.last_message_test)
        client.get_users()
        time.sleep(0.2)
        self.assertEqual("<get_users>", server.last_message_test)
        self.assertEqual("number of connected users: 1\nSabrina", client.last_message_test)
        client.get_list_file()
        time.sleep(0.5)
        self.assertEqual("<get_list_file>", server.last_message_test)
        time.sleep(0.5)
        self.assertEqual("number of files: 2\ntest.txt\ntest1.txt", client.last_message_test)
        server.server_disconnect()


if __name__ == '__main__':
    Test_message.test_message_client()
