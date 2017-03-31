import socket
import sys
import cPickle
import datetime

class Client(object):
	global client
	def __init__(self, data):
		self.data = data

	def call_server(self): 
		Host = socket.gethostbyname(socket.gethostname())
		self.client = socket.socket()
		self.client.connect(('127.0.1.1',1144))
		self.client.send(self.data)

	def receive_and_close(self):
		self.client.recv(1024)
		self.client.close()

def test_client():
	data1 = (1, 9)
	data_send1 = cPickle.dumps(data1)
	data2 = (7, 3)
	data_send2 = cPickle.dumps(data2)
	data3 = (8, 2)
	data_send3 = cPickle.dumps(data3)
	client1 = Client(data_send1)
	client2 = Client(data_send2)
	client3 = Client(data_send3)
	start_time = datetime.datetime.now()
	client1.call_server()
	client2.call_server()
	client3.call_server()
	client1.receive_and_close()
	client2.receive_and_close()
	client3.receive_and_close()
	end_time = datetime.datetime.now()
	difference_time = end_time - start_time
	difference_sec = divmod(difference_time.days * 86400 + 
		difference_time.seconds, 60)
	assert difference_sec[1] <= 3
	
