from client import Client
import unittest
import threading
import datetime

class TestClient(unittest.TestCase):
	
	def test_one(self):
		start_time = datetime.datetime.now()
		client1 = Client(5, 6, '127.0.0.1', 1242)
		client2 = Client(7, 8, '127.0.0.1', 1242)
		client3 = Client(9, 10, '127.0.0.1', 1242)
		client1.result_check()
		client2.result_check()
		client3.result_check()
		end_time = datetime.datetime.now()
		time_difference = end_time - start_time
		time = divmod(
			time_difference.days * 86400 + time_difference.seconds, 
			60
			)
		self.assertTrue(time[1] >= 3)
		

if __name__ == '__main__':
	unittest.main()
	
