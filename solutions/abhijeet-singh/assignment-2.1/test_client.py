from client import Client
from server import Server
from random import randint
import unittest
import threading
import datetime
import argparse
import socket

class TestClient(unittest.TestCase):
	
	def test_one(self):
		clients = []
		start_time = datetime.datetime.now()
		self.ip = socket.gethostbyname(socket.gethostname())
		self.port = 1234
		server = Server(self.ip, self.port)
		server.start()
		for i in range(0, 3):
			thread = threading.Thread(target = self.client_thread)
			thread.start()
			clients.append(thread)
		for client in clients:
			client.join()
		end_time = datetime.datetime.now()
		server.stop()
		time_difference = end_time - start_time
		self.assertTrue(time_difference.total_seconds() <= 3)

	def client_thread(self):
		first_number = randint(0, 1000)
		second_number = randint(0, 1000)
		client = Client(first_number, second_number, self.ip, self.port)
		client.check_result()
	

if __name__ == '__main__':
	unittest.main()
	
